#!/bin/bash
# requested build server
todays_date=$(date +%Y_%m_%d)
curr_time=$(date +%H%M%S)

# Get build parameters as Jenkins parameter environment variable if set
if [[ ! -v SNT_PARAMS ]] ; then
    SNT_PARAMS="PRODUCT=P_0008_x,MODE=2"
fi
PARAMS=$SNT_PARAMS

LOCAL_REQD_BUILD_DIR=/cygdrive/d/build/reqd
NETWORK_REQD_BUILD_DIR=//srv.work.com/work/Engineering/Build/reqd
THIS_LOGFILE=/home/build/reqd/log_test_${todays_date}_${BUILD_NUMBER}.txt

cd $LOCAL_REQD_BUILD_DIR || {
  echo "Can't cd to $LOCAL_REQD_BUILD_DIR" >> $THIS_LOGFILE
  exit
}

BRANCH_FW="master"
TAG_FW=""
BRANCH_DT="master"
TAG_DT=""

PRODUCT="PH_0008_LP_Pixie"
MODE="1"
T="T1000"

# Parse the comma separated NAME=value parameters
regex='(.*)=(.*)'
opt_regex='(OPT_UREG_OVERRIDE_[0-9]+)'
opt_params=""
for param in ${PARAMS//,/ }  ; do
    echo "$param" >> $THIS_LOGFILE
    [[ $param =~ $regex ]] || exit
    p=${BASH_REMATCH[1]}
    q=${BASH_REMATCH[2]}
    if [[ $p =~ ${opt_regex} ]] ; then
        opt_params="${opt_params}CMD_C_FLAGS+=-D$p=$q "
    fi
    declare -g "$p=$q"    
done

repo_name=dsp_${todays_date}

echo "Repo=$repo_name, Jenkins Build number=${BUILD_NUMBER}" >> $THIS_LOGFILE

if [ ! -e $LOCAL_REQD_BUILD_DIR/$repo_name ] ; then
    # Checkout latest master branch from git
    git clone git@gitserv:dsp --recurse-submodules $repo_name  || {
	echo "Could not clone dsp into $repo_name"  >> $THIS_LOGFILE
	exit
    }
else
    cd $LOCAL_REQD_BUILD_DIR/$repo_name
    git pull
fi
cd $LOCAL_REQD_BUILD_DIR/$repo_name
git rev-parse HEAD >> $THIS_LOGFILE
echo "Sync to tag $TAG_FW for $LOCAL_REQD_BUILD_DIR/$repo_name" >> $THIS_LOGFILE
echo "Product=$PRODUCT Mode=$MODE" >> $THIS_LOGFILE

pushd fw
git checkout tags/$TAG_FW
echo "Branch=$BRANCH_FW, Tag=$TAG_FW" >> $THIS_LOGFILE
git checkout $BRANCH_FW
popd

git submodule update --init
git submodule status >> $THIS_LOGFILE
echo "dtools: Branch=$BRANCH_DT Tag=$TAG_DT"  >> $THIS_LOGFILE
pushd fw
(cd dtools; git checkout $BRANCH_DT; git checkout $TAG_DT)
git submodule status >> $THIS_LOGFILE
popd

# --- Generalize the target product
BUILD_TARGET_PRODUCT_Y90=build/work/$PRODUCT/Y90/P$PRODUCT-Y90
BUILD_TARGET_FLASH_Y90=${BUILD_TARGET_PRODUCT_Y90}_PROD.flash
BUILD_TARGET_IMAGE_Y90=${BUILD_TARGET_PRODUCT_Y90}_PROD.update
BUILD_TARGET_STREAM_Y90=${BUILD_TARGET_PRODUCT_Y90}_PROD.stream
BUILD_TARGET_LOG_FILE_Y90=$BUILD_LOG_DIRECTORY/build_log_$PRODUCT.txt
BUILD_TARGET_PRODUCT_OPTIONS="PRODUCT=$PRODUCT THICKNESS=Y90 CMD_C_FLAGS+=-DSUPPORT_HW_MODE=$MODE ${opt_params}"
if [ -n "$USE_COMMIT_DATE" ] ; then
    BUILD_TARGET_PRODUCT_OPTIONS="${BUILD_TARGET_PRODUCT_OPTIONS} USE_COMMIT_DATE=${USE_COMMIT_DATE} "
fi

# -----------------------------

TODAYS_NETWORK_BUILD_DIR=$NETWORK_REQD_BUILD_DIR/${repo_name}_${BUILD_NUMBER}
if [ ! -e $TODAYS_NETWORK_BUILD_DIR ]
then
  echo -e "Creating directory $TODAYS_NETWORK_BUILD_DIR\n"  >> $THIS_LOGFILE
  mkdir $TODAYS_NETWORK_BUILD_DIR 1>> $THIS_LOGFILE 2>> $THIS_LOGFILE || {
    echo "ERROR! Could not create directory $TODAYS_NETWORK_BUILD_DIR"  >> $THIS_LOGFILE
	exit
  }
fi

# --- Build target product firmware
echo "make -j8 all-flash $BUILD_TARGET_PRODUCT_Y90" >> $THIS_LOGFILE
make -j8 all-flash $BUILD_TARGET_PRODUCT_OPTIONS &> $BUILD_TARGET_LOG_FILE_Y90
cp $BUILD_TARGET_LOG_FILE_Y90 $TODAYS_NETWORK_BUILD_DIR 1>> $THIS_LOGFILE 2>> $THIS_LOGFILE || {
  echo "Could not copy $BUILD_TARGET_LOG_FILE_Y90 to $TODAYS_NETWORK_BUILD_DIR"  >> $THIS_LOGFILE  
}
# --- Check to make sure target product build completed, indirection on BUILD_TARGET
for EXT in IMAGE STREAM FLASH ; do
    BUILD_TARGET="BUILD_TARGET_${EXT}_Y90"
if [ -e ${!BUILD_TARGET} ]
then
  echo -e "${!BUILD_TARGET} built successfully\n"  >> $THIS_LOGFILE  
  cp ${!BUILD_TARGET} $TODAYS_NETWORK_BUILD_DIR 1>> $THIS_LOGFILE 2>> $THIS_LOGFILE || {
    echo "Could not copy ${!BUILD_TARGET} to $TODAYS_NETWORK_BUILD_DIR"  >> $THIS_LOGFILE  
  }
else
  echo -e "!!! Build FAILED for ${!BUILD_TARGET} !!!\n"  >> $THIS_LOGFILE  
  result_string=" FAILED!! "  
fi
done
# -----------------------------
cd $LOCAL_REQD_BUILD_DIR || {
  echo "Can't cd to $LOCAL_REQD_BUILD_DIR" >> $THIS_LOGFILE
}

# Deploy $THIS_LOGFILE to srv.work.com/Engineering/Build/reqd/

cp $THIS_LOGFILE $TODAYS_NETWORK_BUILD_DIR
