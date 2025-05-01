#!/bin/bash -v

#output_dir="/Users/esavage/Library/Mobile Documents/com~apple~CloudDocs/T5_Related/IB_margin_files"
output_dir="./IB_margin_files"
#output_dir="/app/IB_margin_files"
mkdir -p "$output_dir"

file_path="$output_dir/$(date +%Y-%m-%d-%H-%M-%S)-margin_futures_fops.html"

curl -o "$file_path" https://www.interactivebrokers.com/en/trading/margin-futures-fops.php || { echo "Download failed"; exit 1; }

# mac format sed invocation
# sed -i '' 's/N\/A/0/g' "$file_path"

# gnu flavored version
sed -i 's/N\/A/0/g' "$file_path"

grep 'N/A' "$file_path"
