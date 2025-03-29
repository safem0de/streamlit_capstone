#!/bin/bash

REGISTRY_URL="http://43.209.49.162:32000"

echo "📦 Getting repository list from $REGISTRY_URL..."
REPOS=$(curl -s "$REGISTRY_URL/v2/_catalog" | jq -r '.repositories[]')

for REPO in $REPOS; do
    echo -e "\n📁 Repository: $REPO"
    
    TAGS=$(curl -s "$REGISTRY_URL/v2/$REPO/tags/list" | jq -r '.tags[]')
    
    for TAG in $TAGS; do
        echo "🔖 Tag: $TAG"

        MANIFEST=$(curl -s -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
            "$REGISTRY_URL/v2/$REPO/manifests/$TAG")
        
        CONFIG_DIGEST=$(echo "$MANIFEST" | jq -r '.config.digest')

        CONFIG=$(curl -s "$REGISTRY_URL/v2/$REPO/blobs/$CONFIG_DIGEST")

        CREATED=$(echo "$CONFIG" | jq -r '.created')
        IMAGE_ID=$(echo "$CONFIG" | jq -r '.config.Image')
        AUTHOR=$(echo "$CONFIG" | jq -r '.author // "unknown"')

        echo "    🕒 Created: $CREATED"
        echo "    🧾 Digest: $CONFIG_DIGEST"
        echo "    👤 Author: $AUTHOR"
    done
done
