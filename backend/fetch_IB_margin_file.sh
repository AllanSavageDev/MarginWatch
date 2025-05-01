#!/bin/bash
set -e

output_dir="/app/IB_margin_files"
mkdir -p "$output_dir"

file_path="$output_dir/$(date +%Y-%m-%d-%H-%M-%S)-margin_futures_fops.html"

echo "Downloading to $file_path"
curl -o "$file_path" https://www.interactivebrokers.com/en/trading/margin-futures-fops.php || {
  echo "Download failed"
  exit 1
}

echo "Download succeeded. Normalizing file..."
sed -i 's/N\/A/0/g' "$file_path"
grep 'N/A' "$file_path" || echo "No 'N/A' entries remaining"
