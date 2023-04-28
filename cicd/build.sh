#!/bin/bash

set -euo pipefail
# ls -al
# cd packages

# echo $BASE_IMAGE

docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY

docker build \
--file="$FOLDER/Dockerfile" \
--build-arg BUILDKIT_INLINE_CACHE=1 \
--build-arg BASE_IMAGE=$BASE_IMAGE \
--cache-from $CI_REGISTRY_IMAGE:latest \
-t $IMAGE_TAG $CONTEXT

docker tag $IMAGE_TAG $IMAGE_TAG:$CI_COMMIT_REF_SLUG-$CI_COMMIT_SHORT_SHA
docker tag $IMAGE_TAG $IMAGE_TAG:latest
docker push --all-tags $IMAGE_TAG

# echo $IMAGE_TAG:$CI_COMMIT_REF_SLUG-$CI_COMMIT_SHORT_SHA
