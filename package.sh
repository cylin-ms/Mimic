#!/bin/bash

# Extract version from mimic.py
VERSION=$(grep '__version__' mimic.py | cut -d '"' -f 2)
PACKAGE_NAME="Mimic"
ZIP_NAME="${PACKAGE_NAME}_v${VERSION}.zip"

echo "📦 Packaging ${PACKAGE_NAME} v${VERSION}..."

# Create a temporary directory
mkdir -p dist/${PACKAGE_NAME}

# Copy files
cp mimic.py dist/${PACKAGE_NAME}/
cp estimate_value.py dist/${PACKAGE_NAME}/
cp download_model.py dist/${PACKAGE_NAME}/
cp requirements.txt dist/${PACKAGE_NAME}/
cp setup.sh dist/${PACKAGE_NAME}/
cp run.sh dist/${PACKAGE_NAME}/
cp setup.bat dist/${PACKAGE_NAME}/
cp run.bat dist/${PACKAGE_NAME}/
cp README.md dist/${PACKAGE_NAME}/
cp MIMIC_USER_GUIDE.md dist/${PACKAGE_NAME}/

# Copy directories
cp -r src dist/${PACKAGE_NAME}/
cp -r templates dist/${PACKAGE_NAME}/
cp -r input dist/${PACKAGE_NAME}/
cp -r models dist/${PACKAGE_NAME}/

# Make scripts executable
chmod +x dist/${PACKAGE_NAME}/*.sh

# Create zip
cd dist
zip -r ../${ZIP_NAME} ${PACKAGE_NAME}
cd ..

# Cleanup
rm -rf dist

echo "✅ Package created: ${ZIP_NAME}"
