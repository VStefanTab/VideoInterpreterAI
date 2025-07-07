# Usage: ./rtsp_to_webcam.sh <rtsp_url> [<device_name>]

# Check if arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <rtsp_url> [<device_name>]"
    echo "Example: $0 rtsp://admin:password@192.168.1.64:554/stream1 my_webcam"
    exit 1
fi

RTSP_URL=$1
DEVICE_NAME=${2:-"rtsp_webcam"}

# Check if v4l2loopback is installed
if ! modinfo v4l2loopback >/dev/null 2>&1; then
    echo "v4l2loopback module not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y v4l2loopback-dkms
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "FFmpeg not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
fi

# Load v4l2loopback module
echo "Loading v4l2loopback module..."
sudo modprobe -r v4l2loopback 2>/dev/null # Remove if already loaded
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="$DEVICE_NAME" exclusive_caps=1

# Check if /dev/video10 was created
if [ ! -e /dev/video10 ]; then
    echo "Failed to create virtual video device."
    exit 1
fi

echo "Streaming RTSP to virtual webcam /dev/video10..."
echo "Press Ctrl+C to stop"

# Start FFmpeg streaming
ffmpeg -i "$RTSP_URL" -fflags nobuffer -flags low_delay -analyzeduration 10 -probesize 32000 -reorder_queue_size 4 -f v4l2 -pix_fmt yuv420p /dev/video10

echo "Stream stopped. To remove the virtual device, run:"
echo "sudo modprobe -r v4l2loopback"