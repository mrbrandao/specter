#!/usr/bin/env bash
name=$(basename "$0")
cmd="$1"
file="$2"
out="$3"
install="$4"
version="$5"
crate_api="https://crates.io/api/v1/crates"
build_root="${BUILD_ROOT:-$HOME/rpmbuild/SOURCES/}"
. specter.conf

#tput colors
yellow=$(tput setaf 148)
green=$(tput setaf 40)
red=$(tput setaf 9)
cyan=$(tput setaf 87)
normal=$(tput sgr0)

missing_packages() {
  #/usr/bin/cargo2rpm --path Cargo.toml buildrequires --with-check
  rpmbuild -ba "$file" 2>&1|grep 'is needed by' > "${name}-$file"
  printf "%s\n" "${green}OK${normal}: Created the file ${yellow}${name}-$file${normal}"
}

get_crate() {
  name="$2"
  version="$3"
  curl -L "$crate_api"/"$name"/"$version"/download -o "$build_root$name-$version.crate"
}

crate_parse() {
  while IFS= read -r line; do
    line=$(echo "$line"|\
      awk -F'is needed by' '{print $1}'|\
      awk '{$1=$1;print}'|\
      sed -E 's/[()~]//g;
          s/^crate/rust-/g;
          s/ with crate/, rust-/g;
          s,/,+,g'|\
      sed -e "s/\(rust[-[:alnum:]*]\{2,\}\)/\1$version/g;
          s/\(rust-\S*\)/\1$out/g"
      )
    echo "$line"
  done < "$file"
}

search_dep() {
  tf="$(mktemp)"
  crate_parse > "$tf"
  printf "%-40s %-10s %-10s %-15s %-10s\n" "Package Name" "Min Ver" "Max Ver" "Available Ver" "Status"
  while read -r line; do
    pkg=$(echo "$line"|awk '{print $1}')
    minver=$(echo "$line"|awk '{print $3}'|sed 's/,//g')
    maxver=$(echo "$line"|awk '{print $6}'|sed 's/,//g')
    avaver=$(search_ver)
    sup=$(check_ver "$avaver" "$minver" "$maxver" "$pkg")
    printf "%-40s %-10s %-10s %-15s %-10s\n" "$pkg" "$minver" "$maxver" "$avaver" "$sup"
  done < "$tf"
  rm -f "$tf"
}

create_build_requires(){
  brf="$(mktemp)"
  crate_parse > "$brf"
  sed -i 's/^/BuildRequires:  /' "$brf"
  cat "$brf"
  rm -f "$brf"
}

check_ver(){
  local sup
  if [[ ("$avaver" > "$minver" || "$avaver" == "$minver" ) && "$avaver" < "$maxver" ]];then
    sup="${green}FOUND${normal}"
    install_dep "$pkg" "$install" "$version"
  elif [[ ( -z "$minver" || -z "$maxver" ) && ( -n "$avaver" ) ]];then
    sup="${green}FOUND${normal}"
    install_dep "$pkg" "$install" "$version"
  else
    sup="${red}LOSS${normal}"
  fi
  printf "%s" "$sup"
}

search_ver(){
  local getver
  for i in $pkg;do
    getver=$(dnf info "$i" 2>&1 /dev/null |\
      grep 'Version'|\
      awk -F':' '{print $2}'|\
      awk '{$1=$1;print}')
    if [ -z "$getver" ]; then
      getver="Missing Version"
      break
    fi
  done
  printf "%s" "$getver"
}

install_dep() {
  flag="$install"
  for i in "$@";do
    if [[ ( -n "$flag" && "$flag" == "-i" ) ]];then
      sudo dnf -y install "$pkg" > /dev/null 2>&1
    fi
  done
}

make_dep() {
  pkg="$2"
  tempfile="$(mktemp)"
  rpm -ivh "$pkg" 2>&1|grep crate > "$tempfile"
  $0 search "$tempfile" -devel -i
  rm -f "$tempfile"
}

copr_add(){
  name="$2"
  project="$3"
  copr-cli add-package-scm --name "$name" \
    --clone-url "$repo" \
    --commit main --method rpkg \
    --spec "$name".spec \
    --subdir rpms/"$name" "$project"
}

copr_build(){
  name="$2"
  project="$3"
  copr-cli buildscm --clone-url "$repo" \
    --commit main --subdir rpms/"$name" \
    --spec "$name".spec --method rpkg "$project"
}

show_missing_declared(){
  rpmbuild -ba "$file" 2>&1|grep "$out"|awk '{$1=$1;print}'|awk '{print $1}'|uniq
}

do_all(){
  pkg="$2"
  ver="$3"
  rust2rpm --no-existence-check "$pkg" "$ver"
  $0 getcrate "$pkg" "$ver"
  if ! rpmbuild -ba rust-"$pkg".spec; then
    $0 init rust-"$pkg".spec
    $0 search specter-rust-"$pkg".spec -devel -i
  fi
}

show_help(){
  printf "Usage:\n"
  declare -A cmd_help=(
    [init]="# generates a specter file for parsing missing dependencies"
    [search]="# search, list or install dependencies"
    [requires]="# print a BuildRequires list"
    [declared]="# list the declared missing dependencies from the spec file"
    [parse]="# print the parsing result from the specter file"
    [getcrate]="# Download a crate file, using name and version"
    [depinstall]="# Install dependencies from an rpm file"
    [copr]="# create and build a package on copr"
    [start]="# start the package project and try to build"
    [copy]="# print the build requires and copy to clipboard"
    [help]="# this help command"
  )
  for key in "${!cmd_help[@]}";do
    value="${cmd_help[$key]}"
    printf "%-20s %s\n" "${green}$key" "${normal}$value"
  done

  echo -ne "Examples:
  # Creating the $name-foo.spec file for parsing dependencies
  ${cyan}${name} ${green}init ${yellow}foo.spec${normal}

  # Using the $name-foo.spec file to search missing packages
  ${cyan}${name} ${green}search ${yellow}$name-foo.spec${normal}

  # search version 3 and appending the word \"-devel\"
  ${cyan}${name} ${green}search ${yellow}${name}-foo.spec ${red}-devel 3${normal}

  # you can automatically install the missing packages when searching
  ${cyan}${name} ${green}search ${yellow}$name-foo.spec ${red}-devel -i${normal}

  # copying the BuildRequires list to the clipboard, to be used on the foo.spec file
  ${cyan}${name} ${green}requires ${yellow}$name-foo.spec${red}|xsel --clipboard${normal}

  # downloading bar-0.1.0.crates to $HOME/rpmbuild/SOURCES/
  ${cyan}${name} ${green}getcrate ${yellow}bar ${red}0.1.0${normal}

  # downloading bar-0.1.0.crate to a custom path
  ${red}BUILD_ROOT=/opt/rpmbuild/SOURCES/ ${cyan}${name} ${green}getcrate ${yellow}bar ${red}0.1.0${normal}

  #listing the still missing packages declared as BuildRequires in foo.spec
  ${cyan}${name} ${green}declared ${yellow}foo.spec${normal}

  # print the $name-foo.spec parsing style
  ${cyan}$name ${green}parse ${yellow}$name-foo.spec ${red}-devel${normal}

  # installing missing depencies from an RPM file
  ${cyan}${name} ${green}depinstall ${yellow}rust-bar-devel.rpm${normal}

  # create and build a package on copr
  ${cyan}${name} ${green}copr ${yellow}rust-bar my-copr-project${normal}

  # start the project and try to build
  ${cyan}${name} ${green}start ${yellow}foo 0.1.0${normal}

  # copy the build requires to the clipboard and print on the stdout
  ${cyan}${name} ${green}copy ${yellow}specter-foo.spec${normal}
"
}

main() {
	if [[ "$#" -lt 2 ]];then
		show_help
		exit 1
	fi
	
  case "$cmd" in
    init)
      missing_packages
    ;;
    search)
      search_dep
    ;;
    requires)
      create_build_requires
    ;;
    copy)
      pkg="$2"
      "$0" requires specter-rust-"$pkg".spec -devel|xsel --clipboard|tee 
    ;;
    declared)
      show_missing_declared
    ;;
    parse)
      crate_parse
    ;;
    getcrate)
      get_crate "$@"
    ;;
    depinstall)
      make_dep "$@"
    ;;
    copr)
      copr_add "$@"
      copr_build "$@"
    ;;
    start)
      do_all "$@"
    ;;
    help)
      show_help
    ;;
    *)
      show_help
    ;;
  esac
}

main "$@"
