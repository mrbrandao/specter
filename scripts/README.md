# Specter Bash Scripts

**Original bash implementation - being migrated to Python**

This directory contains the original bash implementation of specter. While the project is being migrated to Python for better functionality, some features remain bash-only until the migration is complete.

## Overview

Specter started as a bash implementation providing minimal dependencies (bash, standard Unix tools, curl, and dnf) for automating Rust RPM package building. It includes 11 commands covering everything from crate download to Copr builds.

**Current status:**
- **Python has migrated**: `search`, `requires` (use Python - it's better!)
- **Bash still needed for**: `getcrate`, `init`, `start`, `copr`, README generation

## Installation

### Add to PATH

```bash
export PATH="$PATH:/path/to/specter/scripts"
```

Make it permanent by adding to `~/.bashrc` or `~/.bash_profile`:

```bash
echo 'export PATH="$PATH:/path/to/specter/scripts"' >> ~/.bashrc
```

### Use Directly

```bash
cd /path/to/specter/scripts
./specter.sh <command> [arguments]
```

## Configuration

### specter.conf

Configuration file for default settings:

```bash
# specter.conf
repo="https://github.com/yourusername/fedora-rust-packages"
```

### Environment Variables

**BUILD_ROOT**: Directory for crate sources (default: `$HOME/rpmbuild/SOURCES/`)

```bash
# Use custom build directory
BUILD_ROOT=/opt/rpmbuild/SOURCES/ specter.sh getcrate foo 0.1.0
```

## Dependencies

**Required:**
- bash 4.0+
- awk
- sed
- grep
- curl
- dnf
- rpmbuild
- rust2rpm

**Optional:**
- xsel (for clipboard operations)
- copr-cli (for Copr builds)

## Raw Manual Workflow

Before specter, building a Rust RPM required this tedious manual process. This shows what specter automates:

### The Pain: What You'd Do Without Specter

```bash
# Step 1: Download the crate source manually
curl -L https://crates.io/api/v1/crates/myapp/1.0.0/download \
  -o ~/rpmbuild/SOURCES/myapp-1.0.0.crate

# Step 2: Generate initial spec file
cd ~/rpmbuild/SPECS
rust2rpm myapp 1.0.0

# Step 3: Try to build (will fail with missing deps)
rpmbuild -ba rust-myapp.spec

# Output: Error: (crate(foo/default) >= 0.1.0 with crate(foo/default) < 0.2.0~)
#         is needed by rust-myapp-1.0.0-1.fc38.x86_64

# Step 4: Manually identify what package is needed
# You need to know: crate(foo/default) = rust-foo+default-devel in Fedora

# Step 5: Search if package exists
dnf search rust-foo+default-devel
# Package might not be found, try with version numbers
dnf search rust-foo0+default-devel
dnf search rust-foo0.1+default-devel
dnf search rust-foo1+default-devel

# Step 6: Check available version
dnf info rust-foo+default-devel | grep Version
# Output: Version      : 0.1.5

# Step 7: Manually compare versions
# Question: Is 0.1.5 >= 0.1.0 AND < 0.2.0?
# Answer: Yes! (but you had to check manually)

# Step 8: Manually construct BuildRequires line
echo "BuildRequires:  rust-foo+default-devel >= 0.1.0, rust-foo+default-devel < 0.2.0" \
  >> rust-myapp.spec

# Step 9: Install the dependency
sudo dnf install rust-foo+default-devel

# Step 10: Try building again
rpmbuild -ba rust-myapp.spec

# Step 11: Get ANOTHER error for next missing dependency
# Output: Error: (crate(bar/feature) >= 1.5.0 with crate(bar/feature) < 2.0.0~)
#         is needed...

# Step 12: Repeat steps 4-11 for EACH missing dependency...
# For a package with 100 dependencies, you'd repeat this 100 times!
```

### Common Issues in Manual Workflow

**Package naming confusion:**
```bash
# Is it rust-foo-bar or rust-foo_bar?
dnf search rust-foo-bar+default-devel   # try hyphen
dnf search rust-foo_bar+default-devel   # try underscore
dnf search rust-foobar+default-devel    # try combined

# Which version suffix?
dnf search rust-foo+default-devel       # no version
dnf search rust-foo0+default-devel      # version 0
dnf search rust-foo0.1+default-devel    # version 0.1
dnf search rust-foo1+default-devel      # version 1
dnf search rust-foo2+default-devel      # version 2
```

**Version compatibility checking:**
```bash
# Manual version comparison for each dep
# crate(foo) >= 0.14.5 with crate(foo) < 0.15.0
dnf info rust-foo+default-devel | grep Version
# Version: 0.14.8
# Is 0.14.8 >= 0.14.5? Yes
# Is 0.14.8 < 0.15.0? Yes
# Compatible!

# But what about this?
# crate(bar) >= 1.2.3 with crate(bar) < 2.0.0
dnf info rust-bar+default-devel | grep Version
# Version: 0.8.5
# Is 0.8.5 >= 1.2.3? NO!
# Need to find rust-bar1+default-devel instead
```

### What Specter Automates

Instead of all the above:

**Recommended (use Python where migrated):**
```bash
rust2rpm myapp 1.0.0
specter.sh getcrate myapp 1.0.0
specter.sh init rust-myapp.spec
specter search -i specter.sh-rust-myapp.spec -b f38 -o deps.json  # Python - better!
specter requires -i deps.json -c  # Python - better!
# Done! All deps discovered, searched, and BuildRequires copied to clipboard
```

**Or pure bash (quick automation):**
```bash
specter.sh start myapp 1.0.0
# Does everything with bash commands (uses dnf instead of mdapi)
```

## Commands Reference

### Commands Still Needed (Not Yet Migrated to Python)

#### 1. getcrate - Download Crate

**Status:** Not yet in Python, use bash version.

**Purpose:** Download crate source from crates.io.

**Syntax:**
```bash
specter.sh getcrate <package-name> <version>
```

**Parameters:**
- `package-name` - Crate name (without `rust-` prefix)
- `version` - Crate version

**What it does:**
1. Downloads from `https://crates.io/api/v1/crates/<name>/<version>/download`
2. Saves to `$BUILD_ROOT/<name>-<version>.crate`
3. Uses `BUILD_ROOT` environment variable or default `~/rpmbuild/SOURCES/`

**Examples:**

Default location:
```bash
specter.sh getcrate defmac 0.2.1
# Downloads to ~/rpmbuild/SOURCES/defmac-0.2.1.crate
```

Custom location:
```bash
BUILD_ROOT=/opt/rpmbuild/SOURCES/ specter.sh getcrate defmac 0.2.1
# Downloads to /opt/rpmbuild/SOURCES/defmac-0.2.1.crate
```

**Typical usage:**
```bash
specter.sh getcrate foo 1.0.0
rust2rpm foo 1.0.0
```

#### 2. init - Capture Dependency Errors

**Status:** Not yet in Python, use bash version.

**Purpose:** Run rpmbuild and capture missing dependencies to a file for Python to parse.

**Syntax:**
```bash
specter.sh init <spec-file>
```

**Parameters:**
- `spec-file` - The .spec file to build

**What it does:**
1. Runs `rpmbuild -ba` on the spec file (will fail with missing deps)
2. Captures all lines containing `is needed by` using grep
3. Saves to `specter.sh-<spec-file>` for Python CLI to parse

**Example:**
```bash
specter.sh init rust-foo.spec
```

**Output:**
```
OK: Created the file specter.sh-rust-foo.spec
```

**Generated file contents:**
```
(crate(bollard/default) >= 0.14.0 with crate(bollard/default) < 0.15.0~) is needed by rust-foo-1.0.0-1.fc38.x86_64
(crate(criterion/default) >= 0.5.1 with crate(criterion/default) < 0.6.0~) is needed by rust-foo-1.0.0-1.fc38.x86_64
...
```

**Used with Python CLI:**
```bash
specter.sh init rust-foo.spec
specter search -i specter.sh-rust-foo.spec -b f38 -o foo.json  # Python - better!
```

#### 3. start - Complete Automated Workflow

**Status:** Not yet in Python, use bash version.

**Purpose:** Automate the entire process using all bash tools.

**Syntax:**
```bash
specter.sh start <package-name> <version>
```

**Parameters:**
- `package-name` - Crate name
- `version` - Crate version

**What it does:**
1. Generates spec with `rust2rpm --no-existence-check`
2. Downloads crate with `getcrate`
3. Attempts build with `rpmbuild` (will fail)
4. If build fails, runs `init` to capture errors
5. Runs bash `search` with auto-install (uses dnf, not mdapi)

**Example:**
```bash
specter.sh start chariott 0.1.0
```

**Equivalent to:**
```bash
rust2rpm --no-existence-check chariott 0.1.0
specter.sh getcrate chariott 0.1.0
rpmbuild -ba rust-chariott.spec
# (if fails)
specter.sh init rust-chariott.spec
specter.sh search specter.sh-rust-chariott.spec -devel -i
```

**Then add BuildRequires and rebuild:**
```bash
specter.sh requires specter.sh-rust-chariott.spec -devel >> rust-chariott.spec
rpmbuild -ba rust-chariott.spec
```

**Use case:** Quick automation for simple packages with few dependencies.

**Note:** Uses bash search (dnf-based) not Python search (mdapi-based). For better results, use the recommended workflow with Python search.

#### 4. copr - Build on Copr

**Status:** Not yet in Python, use bash version.

**Purpose:** Create and build a package on Copr.

**Syntax:**
```bash
specter.sh copr <package-name> <copr-project>
```

**Parameters:**
- `package-name` - Name of the package (without `rust-` prefix)
- `copr-project` - Your Copr project name

**What it does:**
1. Adds the package to Copr using `copr-cli add-package-scm`
2. Triggers a build using `copr-cli buildscm`
3. Uses `$repo` from `specter.conf` for git repository

**Example:**
```bash
# Requires specter.conf with: repo="https://github.com/user/fedora-rust"
specter.sh copr chariott my-rust-packages
```

**Requirements:**
- `copr-cli` installed and configured
- `repo` variable in `specter.conf`
- Package in git repository at `rpms/<package-name>/`

**Configuration needed:**
```bash
# ~/.config/copr
[copr-cli]
username = yourusername
login = your_api_login_token
token = your_api_token
copr_url = https://copr.fedorainfracloud.org
```

### Commands Superseded by Python (Bash versions still work)

#### 5. search - Search Dependencies (Bash Version)

**Status:** Migrated to Python. Use `specter search` instead (better!).

**Purpose:** Search Fedora repositories for dependencies using dnf and optionally install them.

**Syntax:**
```bash
specter.sh search <specter-file> [suffix] [install-flag] [version]
```

**Why Python is better:**
- Uses mdapi API (faster than dnf commands)
- Accurate version comparison (`packaging` library vs string comparison)
- Rich formatted output
- JSON output for automation

**Example:**
```bash
# Bash version (slower, string comparison)
specter.sh search specter.sh-rust-foo.spec -devel

# Python version (better!)
specter search -i specter.sh-rust-foo.spec -b f38 -o foo.json
```

#### 6. requires - Generate BuildRequires (Bash Version)

**Status:** Migrated to Python. Use `specter requires` instead (better!).

**Purpose:** Generate BuildRequires statements from parsed dependencies.

**Syntax:**
```bash
specter.sh requires <specter-file> [suffix] [version]
```

**Why Python is better:**
- Reads JSON from Python search
- Better formatting options
- Cross-platform clipboard support

**Example:**
```bash
# Bash version
specter.sh requires specter.sh-rust-foo.spec -devel

# Python version (better!)
specter requires -i foo.json -p -c
```

### Utility Commands

#### 7. parse - Display Parsing Result

**Purpose:** Show how the specter file will be parsed without searching.

**Syntax:**
```bash
specter.sh parse <specter-file> [suffix] [version]
```

**Example:**
```bash
specter.sh parse specter.sh-rust-foo.spec -devel
```

**Output:**
```
rust-bar+default-devel >= 0.1.0, rust-bar+default-devel < 0.2.0
rust-baz+feature-devel >= 1.5.0, rust-baz+feature-devel < 2.0.0
```

**Use case:** Verify the parsing logic before searching.

#### 8. declared - List Missing Dependencies

**Purpose:** List packages still missing from a spec file (after BuildRequires are declared).

**Syntax:**
```bash
specter.sh declared <spec-file> [suffix]
```

**Example:**
```bash
specter.sh declared rust-foo.spec -devel
```

**Output:**
```
rust-bar+default-devel
rust-baz+feature-devel
```

**Use case:** After adding BuildRequires to spec, check what still needs to be installed or built.

#### 9. depinstall - Install from RPM File

**Purpose:** Install dependencies listed in an RPM file's requires.

**Syntax:**
```bash
specter.sh depinstall <rpm-file>
```

**Example:**
```bash
specter.sh depinstall rust-foo-devel-1.0.0-1.fc38.x86_64.rpm
```

**Use case:** Installing build dependencies for locally built RPMs.

#### 10. copy - Generate and Copy to Clipboard

**Purpose:** Generate BuildRequires and copy to clipboard in one command.

**Syntax:**
```bash
specter.sh copy <package-name>
```

**Example:**
```bash
specter.sh copy foo
```

**Output:**
```
BuildRequires:  rust-bar+default-devel >= 0.1.0, rust-bar+default-devel < 0.2.0
BuildRequires:  rust-baz+feature-devel >= 1.5.0, rust-baz+feature-devel < 2.0.0
(also copied to clipboard)
```

**Requirements:** `xsel` package must be installed.

```bash
sudo dnf install xsel
```

#### 11. help - Show Help

**Purpose:** Display usage information and examples.

**Syntax:**
```bash
specter.sh help
```

## Helper Scripts

### specrender.py - README Generator

**Status:** Not yet migrated to Python CLI.

**Purpose:** Generate README files from Jinja2 templates for package documentation.

**Location:** `scripts/specrender.py`

**Syntax:**
```bash
python3 specrender.py [OPTIONS] <requires...>
```

**Options:**
- `--name NAME` - Package name (required)
- `--ver VERSION` - Package version (optional)
- `--dest FILE` - Output filename (default: `README.md`)
- `--path TEMPLATE` - Template file path (default: `~/dev/gen/specter/templates/rust_readme.j2`)
- `--min` - Use versioned package names (e.g., `rust-foo2`)

**Parameters:**
- `requires...` - List of required package names (space-separated)

**Examples:**

Basic usage:
```bash
python3 specrender.py --name chariott --ver 0.1.0 \
    criterion prost tensorflow tonic bollard
```

Custom destination:
```bash
python3 specrender.py --name myapp --ver 1.0.0 \
    --dest ~/packages/myapp/README.md \
    foo bar baz
```

**Output:**
Creates a README.md with:
- Package information header
- Copr build status link
- Dependency tree with checkboxes
- Build instructions

## Workflow Examples

### 1. Recommended: Use Python Where Available

Best results using bash for features not yet migrated, Python for improved features:

```bash
# Download and setup (bash - not yet in Python)
rust2rpm myapp 1.0.0
specter.sh getcrate myapp 1.0.0

# Capture errors (bash - not yet in Python)
specter.sh init rust-myapp.spec

# Search using mdapi (Python - better than bash!)
specter search -i specter.sh-rust-myapp.spec -b f38 -o myapp.json

# Generate BuildRequires (Python - better formatting!)
specter requires -i myapp.json -c

# Paste into spec
vim rust-myapp.spec

# Build
sudo dnf builddep rust-myapp.spec
rpmbuild -ba rust-myapp.spec
```

### 2. Pure Bash Workflow (Quick Automation)

Using only bash commands (dnf-based):

```bash
# One command does everything (uses bash search with dnf)
specter.sh start myapp 1.0.0

# Add BuildRequires and build
specter.sh requires specter.sh-rust-myapp.spec -devel >> rust-myapp.spec
rpmbuild -ba rust-myapp.spec
```

### 3. Complex Package with README Tracking

For packages with many dependencies (like chariott with 100+ deps):

```bash
# Create package directory structure
mkdir -p ~/dev/redhat/pkgs/rpm-rust-chariott/rpms/chariott
cd ~/dev/redhat/pkgs/rpm-rust-chariott/rpms/chariott

# Initial setup (bash)
rust2rpm chariott 0.1.0
specter.sh getcrate chariott 0.1.0

# Capture dependencies (bash)
specter.sh init rust-chariott.spec

# Search dependencies (Python - better!)
specter search -i specter.sh-rust-chariott.spec -b f38 -o chariott.json

# Generate README to track progress (bash - not yet in Python)
python3 ~/dev/gen/specter/scripts/specrender.py \
    --name chariott --ver 0.1.0 \
    criterion prost tensorflow tonic bollard ndarray metrics-util

# Edit README.md to add full dependency tree
vim README.md

# Build each missing dependency recursively
# Mark progress in README: [ ] -> [p] -> [x]
```

## Parsing Logic

Understanding how specter transforms crate names to RPM package names.

### Step-by-Step Transformation

**Input:** rpmbuild error message
```
(crate(foo/default) >= 0.1.0 with crate(foo/default) < 0.2.0~) is needed by rust-bar-1.0.0-1.fc38.x86_64
```

**Step 1:** Extract the requirement (before `is needed by`)
```bash
awk -F'is needed by' '{print $1}'
```
Result: `(crate(foo/default) >= 0.1.0 with crate(foo/default) < 0.2.0~)`

**Step 2:** Remove leading/trailing whitespace
```bash
awk '{$1=$1;print}'
```

**Step 3:** Remove parentheses and tildes, replace crate with rust-
```bash
sed -E 's/[()~]//g; s/^crate/rust-/g; s/ with crate/, rust-/g'
```
Result: `rust-foo/default >= 0.1.0, rust-foo/default < 0.2.0`

**Step 4:** Replace `/` with `+` (feature separator)
```bash
sed 's,/,+,g'
```
Result: `rust-foo+default >= 0.1.0, rust-foo+default < 0.2.0`

**Step 5:** Append suffix (e.g., `-devel`)
```bash
sed "s/\(rust-\S*\)/\1-devel/g"
```
Result: `rust-foo+default-devel >= 0.1.0, rust-foo+default-devel < 0.2.0`

**Step 6:** Append version number if specified (e.g., `2` for 2.x packages)
```bash
sed "s/\(rust[-[:alnum:]*]\{2,\}\)/\12/g"
```
Result: `rust-foo2+default-devel >= 0.1.0, rust-foo2+default-devel < 0.2.0`

### Complete sed/awk Pipeline

The `crate_parse()` function:

```bash
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
```

## Why Python Is Better (When Available)

### Bash Limitations

**Version comparison issues:**
```bash
# Bash uses lexicographic (string) comparison
# This fails: "0.9.0" > "0.10.0" (wrong!)
# Actual: 0.9.0 < 0.10.0

# Example bash comparison:
if [[ "0.9.0" > "0.10.0" ]]; then
  echo "Bash thinks 0.9.0 is greater!"  # This executes (wrong!)
fi
```

**Performance issues:**
```bash
# Bash search uses dnf for each package
dnf info rust-foo+default-devel  # Slow command
dnf info rust-bar+default-devel  # Another slow command
# For 100 packages, this takes minutes
```

**Fragile parsing:**
```bash
# sed/awk pipelines can break on edge cases
# Complex version constraints might fail
```

### Python Advantages

**Accurate version comparison:**
```python
from packaging.version import Version
Version("0.9.0") < Version("0.10.0")  # True (correct!)
```

**Fast API calls:**
```python
# Python uses mdapi API
requests.get("https://mdapi.fedoraproject.org/f38/pkg/rust-foo+default-devel")
# Fast HTTP request, can parallelize
```

**Robust parsing:**
```python
# Python parsing handles edge cases better
# Structured code, testable, maintainable
```

**Better output:**
- Rich formatted tables
- JSON for automation
- Cross-platform clipboard
- Progress indicators

## Migration Status

| Feature | Bash | Python | Status |
|---------|------|--------|--------|
| Download crates | `getcrate` | - | Use bash |
| Capture errors | `init` | - | Use bash |
| Parse dependencies | `search` | `search` | **Use Python (better!)** |
| Search packages | `search` | `search` | **Use Python (better!)** |
| Version comparison | String-based | `packaging` lib | **Use Python (better!)** |
| Generate BuildRequires | `requires` | `requires` | **Use Python (better!)** |
| Complete automation | `start` | - | Use bash |
| Copr integration | `copr` | - | Use bash |
| README generation | `specrender.py` | - | Use bash |

## Troubleshooting

### specter.sh not found

**Problem:** `bash: specter.sh: command not found`

**Solution:**
```bash
# Use full path
/path/to/specter/scripts/specter.sh help

# Or add to PATH
export PATH="$PATH:/path/to/specter/scripts"

# Or create symlink
sudo ln -s /path/to/specter/scripts/specter.sh /usr/local/bin/specter.sh
```

### Permission denied

**Problem:** `bash: ./specter.sh: Permission denied`

**Solution:**
```bash
chmod +x specter.sh
```

### xsel not found

**Problem:** `copy` command fails with `xsel: command not found`

**Solution:**
```bash
# Install xsel
sudo dnf install xsel

# Or use manual clipboard (Ctrl+C after running)
specter.sh requires specter.sh-rust-foo.spec -devel
```

### BUILD_ROOT not set

**Problem:** `getcrate` downloads to wrong location

**Solution:**
```bash
# Set BUILD_ROOT explicitly
BUILD_ROOT=/opt/rpmbuild/SOURCES/ specter.sh getcrate foo 1.0.0

# Or set as environment variable
export BUILD_ROOT=/opt/rpmbuild/SOURCES/
specter.sh getcrate foo 1.0.0

# Or add to ~/.bashrc
echo 'export BUILD_ROOT=/opt/rpmbuild/SOURCES/' >> ~/.bashrc
```

### Version comparison issues

**Problem:** Bash string comparison doesn't handle versions correctly

**Example:**
```bash
# Bash thinks: "0.9.0" > "0.10.0" (lexicographic comparison)
# Actual: 0.9.0 < 0.10.0
```

**Solution:**
Use the Python CLI which has accurate version comparison:

```bash
# Instead of bash search:
specter.sh search specter.sh-rust-foo.spec -devel

# Use Python search:
specter search -i specter.sh-rust-foo.spec -b f38 -o foo.json
```

### Copr command fails

**Problem:** `copr` command errors with authentication or repo issues

**Solution:**
```bash
# Configure copr-cli first
copr-cli --help

# Check your config
cat ~/.config/copr

# Set up specter.conf with your repo
echo 'repo="https://github.com/yourusername/fedora-rust"' > specter.conf

# Verify your repo structure
# Should have: rpms/<package-name>/<package-name>.spec
```

## See Also

- **Main README**: [../README.md](../README.md) - Python CLI documentation and project overview
- **Template System**: [../templates/rust_readme.j2](../templates/rust_readme.j2) - Jinja2 template for README generation
- **Python Implementation**: [../src/specter/](../src/specter/) - Modern Python CLI source code
- **Configuration**: [specter.conf](specter.conf) - Bash scripts configuration file
- **Fedora Guidelines**: [Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/)

## Contributing

The bash implementation serves as the original codebase while Python migration is in progress. New features are being added to the Python CLI. However, improvements to bash-specific features (getcrate, init, copr, README generation) are welcome until they're migrated to Python!
