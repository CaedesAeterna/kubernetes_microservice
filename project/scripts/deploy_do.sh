#!/bin/bash
set -e

# Configuration
REGISTRY_PREFIX="registry.digitalocean.com/tiamat"

# 1. Read current version
if [ ! -f VERSION ]; then
    echo "VERSION file not found!"
    exit 1
fi
current_ver=$(cat VERSION)
echo "Current Version: $current_ver"

# 2. Increment version (Logic: Bump Patch. If Patch > 99, Bump Minor and Reset Patch)
IFS='.' read -r -a parts <<< "$current_ver"
major=${parts[0]}
minor=${parts[1]}
patch=${parts[2]}

patch=$((patch + 1))

if [ "$patch" -gt 99 ]; then
    patch=0
    minor=$((minor + 1))
fi

new_ver="${major}.${minor}.${patch}"

echo "Bumping to: $new_ver"

# 2.5 Ensure Infrastructure (Mongo RS) is ready
echo "------------------------------------------------"
echo "Verifying Infrastructure..."
./scripts/init_mongo_rs.sh
echo "------------------------------------------------"

# 3. Dynamic Build, Tag, Push & Deploy
services_dir="services"

echo "Detected Services:"
ls $services_dir

for service_path in "$services_dir"/*; do
    if [ -d "$service_path" ]; then
        service_name=$(basename "$service_path")
        
        echo "------------------------------------------------"
        echo "Processing Service: $service_name"
        
        # Local tag and Remote tag
        local_image="$service_name:$new_ver"
        remote_image="$REGISTRY_PREFIX/$service_name:$new_ver"
        
        # Build
        echo "Building Image: $local_image"
        docker build -t "$local_image" "$service_path"
        
        # Tag for Remote Registry
        echo "Tagging: $remote_image"
        docker tag "$local_image" "$remote_image"
        
        # Push to DigitalOcean Registry
        echo "Pushing to Registry: $remote_image"
        docker push "$remote_image"
        
        # Update Kubernetes Deployment
        echo "Updating Cluster Deployment..."
        if kubectl get deployment "$service_name" -n app > /dev/null 2>&1; then
            # Update existing deployment to use the new image from the registry
            kubectl set image "deployment/$service_name" "$service_name=$remote_image" -n app
        else
            echo "Deployment '$service_name' not found. Creating from manifest..."
            if [ -f "k8s/apps/$service_name.yaml" ]; then
                # Apply the base manifest first
                kubectl apply -f "k8s/apps/$service_name.yaml"
                # Then set the image to the one we just pushed
                kubectl set image "deployment/$service_name" "$service_name=$remote_image" -n app
            else
                echo "Error: Manifest 'k8s/apps/$service_name.yaml' not found. Cannot deploy new service."
            fi
        fi
    fi
done

# 4. Save new version
echo $new_ver > VERSION
echo "------------------------------------------------"
echo "Deployment of v$new_ver initiated."

# 5. Dynamic Wait for Rollout
for service_path in "$services_dir"/*; do
    if [ -d "$service_path" ]; then
        service_name=$(basename "$service_path")
        if kubectl get deployment "$service_name" -n app > /dev/null 2>&1; then
            echo "Waiting for rollout: $service_name"
            kubectl rollout status "deployment/$service_name" -n app
        fi
    fi
done

echo "Done! Application is now running version $new_ver on DigitalOcean."
