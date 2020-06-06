pushd %~dp0
docker build -t telegram-forwarding .
docker run -it --rm telegram-forwarding --api_id=<API_ID> --api_hash=<API_HASH> --phone=<PHONE_NUMBER>
popd
PAUSE
