#! /bin/bash

# Deploy container image to ECS via ECR

# Tag, Push and Deploy only if it's not a pull request
if [ -z "$TRAVIS_PULL_REQUEST" ] || [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  # Push only if we're testing the master branch
   if [ "$TRAVIS_BRANCH" == "master" ]; then
    echo Getting the ECR login...
    eval $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)

    REMOTE_DOCKER_PATH="$DOCKER_REPO"/"$DOCKER_REPO_NAMESPACE"/"$DOCKER_IMAGE"
    TAG=travis-buildnum-"$TRAVIS_BUILD_NUMBER"
    echo Tagging with "$TAG"
    docker tag "$DOCKER_IMAGE":latest "$REMOTE_DOCKER_PATH":"$TAG"
    echo Running docker push command...
    docker push "$REMOTE_DOCKER_PATH":"$TAG"

    TAG=latest
    echo Tagging with "$TAG"
    docker tag "$DOCKER_IMAGE":latest "$REMOTE_DOCKER_PATH":"$TAG"
    echo Running docker push command...
    docker push "$REMOTE_DOCKER_PATH":"$TAG"

    echo Running ecs-deploy.sh script...
    ./bin/ecs-deploy.sh  \
     -n "$ECS_SERVICE_NAME" \
     -c "$ECS_CLUSTER"   \
     -i "$REMOTE_DOCKER_PATH":latest \
     --timeout 300
   else
     echo "Skipping deploy because branch is not master"
  fi
else
  echo "Skipping deploy because it's a pull request"
fi
