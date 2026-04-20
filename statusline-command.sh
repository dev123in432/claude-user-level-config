#!/usr/bin/env bash
input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // .workspace.current_dir // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
rate5h=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
rate7d=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

# basename only, not full path
folder=$(basename "$cwd")

# ANSI color codes
reset='\033[0m'
bold='\033[1m'
dim='\033[2m'
cyan='\033[36m'
yellow='\033[33m'
blue='\033[34m'
sep="${dim} | ${reset}"

out=""
[ -n "$folder" ] && out="${bold}${cyan}${folder}${reset}"
[ -n "$model" ] && out="${out}${sep}${blue}${model}${reset}"
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  out="${out}${sep}${yellow}ctx: ${used_int}%${reset}"
fi
if [ -n "$rate5h" ]; then
  rate_int=$(printf '%.0f' "$rate5h")
  if [ "$rate_int" -ge 80 ]; then
    color='\033[31m'
  elif [ "$rate_int" -ge 50 ]; then
    color="$yellow"
  else
    color='\033[32m'
  fi
  label="${rate_int}%"
  if [ -n "$rate7d" ]; then
    rate7d_int=$(printf '%.0f' "$rate7d")
    label="${rate_int}%, ${rate7d_int}%"
  fi
  out="${out}${sep}${color}usage: ${label}${reset}"
fi

printf "%b" "$out"
