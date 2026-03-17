# Specter

**A personification of a spec file - Automate RPM dependency management for Fedora**

Specter simplifies RPM package creation for Rust projects by automating dependency discovery, BuildRequires generation, and package availability checking. It eliminates the manual, iterative process of building → failing → searching → installing → repeat.

## Overview

When building Rust RPMs for Fedora, you typically face a painful workflow:
1. Generate a spec file with `rust2rpm`
2. Try to build with `rpmbuild` - it fails with missing dependencies
3. Manually convert crate names to Fedora package names
4. Search if packages exist in Fedora repos
5. Add BuildRequires to the spec file
6. Repeat for every missing dependency...

**Specter automates all of this.** It parses build failures, converts crate names to RPM package names, searches Fedora repositories, and generates properly formatted BuildRequires statements—all in one go.

### Vision

Initially created for Rust packages, specter is designed as a **generic suite for identifying dependency hell** when building packages. The project aims to expand support to:
- **Current**: Rust packages (crate name → `rust-*` packages)
- **Future**: Python packages (PyPI → `python3-*` packages)
- **Future**: Go modules (go.mod → `golang-*` packages)
- **Goal**: Universal dependency resolution framework for any language ecosystem

### Implementation Status

Specter **started as a bash implementation** and is currently **being migrated to Python**:

**Python CLI (use when available):**
- `search` - Parse dependencies and search mdapi (replaces bash search)
- `requires` - Generate BuildRequires from JSON (replaces bash requires)
- Better parsing with Python vs sed/awk
- mdapi API (faster) vs dnf commands (slower)
- Accurate version comparison using `packaging` library
- Rich formatted output with tables and colors
- JSON output for automation

**Bash scripts (use for features not yet migrated):**
- `getcrate` - Download crates from crates.io
- `init` - Capture rpmbuild errors
- `start` - Complete automation workflow
- `copr` - Build on Copr
- `specrender.py` - Generate README from templates
- Other utility commands

**Recommended workflow**: Use bash for what's not yet in Python (getcrate, init), then use Python for what's been migrated (search, requires).

## The Problem

When building a Rust RPM, you'll encounter errors like this:

```bash
$ rpmbuild -ba rust-chariott.spec
error: Failed build dependencies:
    (crate(bollard/default) >= 0.14.0 with crate(bollard/default) < 0.15.0~) is needed by chariott-0.1.0-1.fc38.x86_64
    (crate(criterion/async_tokio) >= 0.5.1 with crate(criterion/async_tokio) < 0.6.0~) is needed by chariott-0.1.0-1.fc38.x86_64
    (crate(prost/default) >= 0.11.0 with crate(prost/default) < 0.12.0~) is needed by chariott-0.1.0-1.fc38.x86_64
    ...
```

To fix this manually, you'd need to:
1. Identify that `crate(bollard/default)` translates to `rust-bollard+default-devel`
2. Search Fedora repos: `dnf search rust-bollard+default-devel`
3. Check version compatibility
4. Add the BuildRequires line to your spec
5. Repeat for each dependency
6. Handle version mismatches (e.g., `rust-bollard0.14+default-devel` for versioned packages)

**This is tedious, error-prone, and time-consuming when dealing with 100+ dependencies.**

## How Specter Solves This

```
rust2rpm    →    specter.sh      →    specter.sh    →    specter        →    specter
                 getcrate             init               search              requires
   │                 │                    │                   │                   │
   │                 │                    │                   │                   └─> BuildRequires ready
   │                 │                    │                   └─> JSON with package status (mdapi)
   │                 │                    └─> Capture dependency errors
   │                 └─> Download crate source
   └─> Generate initial spec file

OR use specter.sh start (does all of the above automatically with bash search/dnf)
```

Key features:
- **Automatic crate-to-RPM name conversion**: `crate(foo/default)` → `rust-foo+default-devel`
- **mdapi integration**: Queries Fedora's metadata API to check package availability
- **Version comparison**: Validates that available versions satisfy requirements using `packaging` library
- **BuildRequires generation**: Properly formatted statements ready to paste
- **Clipboard integration**: Copy results directly to clipboard
- **JSON output**: Machine-readable results for automation
- **README generation**: Track dependency trees with checkboxes

## Installation

### Python CLI (Required for search/requires)

**Option 1: Using Makefile (recommended)**
```bash
cd /path/to/specter
make pip_install
```

**Option 2: Direct pip install**
```bash
cd /path/to/specter
pip install --editable .
```

**Uninstall:**
```bash
make pip_uninstall
# or
pip uninstall specter
```

**Dependencies:**
- Python 3.8+
- click >= 8.1.7
- requests >= 2.31.0
- rich >= 13.6.0
- pyperclip >= 1.8.2
- packaging >= 20.0

### Bash Scripts (Required for getcrate/init)

**Option 1: Using Makefile (recommended)**

Install to `~/bin`:
```bash
cd /path/to/specter
make install
```

Or create symlinks for development:
```bash
cd /path/to/specter
make link
```

Uninstall:
```bash
make uninstall
```

**Option 2: Add to PATH**
```bash
export PATH="$PATH:/path/to/specter/scripts"
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export PATH="$PATH:/path/to/specter/scripts"' >> ~/.bashrc
```

**External tools required:**
- `rust2rpm` - Generate initial spec files
- `rpmbuild` - Build RPM packages
- `curl` - Download crates
- `dnf` - Package management

## Quick Start

### Option 1: Recommended Workflow (Use Python where available)

Use bash for features not yet migrated, Python for improved features:

```bash
# 1. Generate spec file
rust2rpm chariott 0.1.0

# 2. Download crate source (bash - not yet in Python)
specter.sh getcrate chariott 0.1.0

# 3. Capture dependency errors (bash - not yet in Python)
specter.sh init rust-chariott.spec
# Creates: specter.sh-rust-chariott.spec

# 4. Parse and search Fedora repos (Python - better than bash version!)
specter search -i specter.sh-rust-chariott.spec -b f38 -o chariott-deps.json

# 5. Generate BuildRequires (Python - better formatting than bash!)
specter requires -i chariott-deps.json -p

# 6. Copy to clipboard (Python)
specter requires -i chariott-deps.json -c

# 7. Edit spec and paste
vim rust-chariott.spec  # paste from clipboard

# 8. Install dependencies and build
sudo dnf builddep rust-chariott.spec
rpmbuild -ba rust-chariott.spec
```

### Option 2: Pure Bash (Complete automation)

Use `specter.sh start` for quick automation with all bash commands:

```bash
# One command does everything (uses bash search with dnf)
specter.sh start chariott 0.1.0

# This automatically:
# 1. Runs rust2rpm to generate spec
# 2. Downloads crate with getcrate
# 3. Tries rpmbuild (will fail)
# 4. Captures errors with init
# 5. Searches and installs deps with bash search (dnf-based)

# Then add BuildRequires and rebuild
specter.sh requires specter.sh-rust-chariott.spec -devel >> rust-chariott.spec
rpmbuild -ba rust-chariott.spec
```

**Note:** Option 1 is recommended because Python search uses mdapi (faster) and has better version comparison.

## Python CLI Usage

The Python CLI provides improved implementations of parsing and searching features.

### `specter search` - Parse and Search Dependencies

**Better than bash version:** Uses mdapi API instead of dnf commands, accurate version comparison with `packaging` library.

**Syntax:**
```bash
specter search [OPTIONS]
```

**Options:**
- `-i, --input PATH` - Input file with dependency errors (created by `specter.sh init`) (default: `/tmp/test`)
- `-b, --branch BRANCH` - Fedora branch to search (default: `f38`)
- `-l, --list` - List dependencies without searching
- `-o, --out FILE` - Save search results to JSON file (default: `specter-search.json`)

**Examples:**

```bash
# Parse bash output and search f38 repos via mdapi
specter search -i specter.sh-rust-foo.spec -b f38 -o deps.json

# Just list what dependencies were found (no search)
specter search -i specter.sh-rust-foo.spec -l

# Search rawhide
specter search -i specter.sh-rust-foo.spec -b rawhide -o deps.json

# Search f39
specter search -i specter.sh-rust-foo.spec -b f39 -o deps.json
```

**What it does:**
1. Reads the file created by `specter.sh init` (raw rpmbuild errors)
2. Parses lines containing dependency requirements
3. Converts crate syntax to Fedora package names (e.g., `(crate(foo/default)` → `rust-foo+default-devel`)
4. Queries mdapi to check if packages exist in Fedora repos
5. Validates version compatibility using the `packaging` library
6. Tries versioned package variants if initial search fails (e.g., `rust-foo2+default-devel`)
7. Saves results to JSON file with status: `FOUND`, `NOT` (not found), or `MISS` (version mismatch)

**Output:**
```
searching: specter.sh-rust-foo.spec

Package Name                             Min Ver    Max Ver    Available Ver   Status
────────────────────────────────────────────────────────────────────────────────────────
rust-foo+default-devel                   0.1.0      0.2.0      0.1.5           FOUND
rust-bar+feature-devel                   1.5.0      2.0.0      Not Found       NOT
```

### `specter requires` - Generate BuildRequires

Reads JSON from Python search, better formatting options.

**Syntax:**
```bash
specter requires [OPTIONS]
```

**Options:**
- `-i, --input FILE` - Input JSON file from search (default: `specter-search.json`)
- `-p, --print` - Print BuildRequires to stdout
- `-l, --list` - List searched packages with status
- `-c, --clip` - Copy BuildRequires to clipboard

**Examples:**

```bash
# Print BuildRequires to stdout
specter requires -i deps.json -p

# List all packages with their status
specter requires -i deps.json -l

# Copy to clipboard for pasting into spec file
specter requires -i deps.json -c

# Print AND copy to clipboard
specter requires -i deps.json -p -c
```

**What it does:**
1. Reads the JSON file from `specter search`
2. Filters for packages with status `FOUND`
3. Generates properly formatted BuildRequires statements:
   ```
   BuildRequires:  rust-foo+default-devel >= 0.1.0, rust-foo+default-devel < 0.2.0
   ```
4. Optionally copies to clipboard (using pyperclip) or prints to stdout

## Bash Script Commands

The bash scripts provide features not yet migrated to Python.

### Primary Commands (Not Yet in Python)

**`specter.sh getcrate`** - Download crate from crates.io
```bash
specter.sh getcrate <package-name> <version>
```

**`specter.sh init`** - Capture dependency errors from rpmbuild
```bash
specter.sh init <spec-file>
```
Creates: `specter.sh-<spec-file>` for Python to parse

**`specter.sh start`** - Complete automation (all bash)
```bash
specter.sh start <package-name> <version>
```
Internally calls: rust2rpm → getcrate → rpmbuild → init → search (bash/dnf version)

### Other Bash Commands

For complete bash script documentation including `search` (bash version), 
`requires` (bash version), `parse`, `declared`, `depinstall`, `copr`, `copy`, 
and the **raw manual command workflow**, see [scripts/README.md](scripts/README.md).

## Complete Workflow: From Crate to Built RPM

### Recommended: Use Python Where Available

Best results using bash for features not yet migrated, Python for improved features:

**Step 1: Generate Spec File**
```bash
rust2rpm myapp 1.0.0
# Creates: rust-myapp.spec
```

**Step 2: Download Crate Source (Bash - not yet in Python)**
```bash
specter.sh getcrate myapp 1.0.0
# Downloads to: ~/rpmbuild/SOURCES/myapp-1.0.0.crate
```

**Step 3: Capture Dependency Errors (Bash - not yet in Python)**
```bash
specter.sh init rust-myapp.spec
# Creates: specter.sh-rust-myapp.spec
```

This runs rpmbuild which **will fail** - that's expected and intentional! It captures the error output.

**Step 4: Search Dependencies (Python - better than bash!)**
```bash
specter search -i specter.sh-rust-myapp.spec -b f38 -o myapp-deps.json
```

Output:
```
searching: specter.sh-rust-myapp.spec

Package Name                             Min Ver    Max Ver    Available Ver   Status
────────────────────────────────────────────────────────────────────────────────────────
rust-foo+default-devel                   0.1.0      0.2.0      0.1.5           FOUND
rust-bar+feature-devel                   1.5.0      2.0.0      1.8.2           FOUND
```

**Step 5: Generate BuildRequires (Python - better than bash!)**
```bash
specter requires -i myapp-deps.json -p -c
```

Output (also copied to clipboard):
```
BuildRequires:  rust-foo+default-devel >= 0.1.0, rust-foo+default-devel < 0.2.0
BuildRequires:  rust-bar+feature-devel >= 1.5.0, rust-bar+feature-devel < 2.0.0
```

**Step 6: Update Spec File**
```bash
vim rust-myapp.spec
# Paste the BuildRequires lines (already in clipboard)
```

**Step 7: Install Dependencies and Build**
```bash
# Install the dependencies
sudo dnf builddep rust-myapp.spec

# Build successfully
rpmbuild -ba rust-myapp.spec
```

### Alternative: Pure Bash (Quick Automation)

For quick automation using all bash commands:

```bash
# One command does everything
specter.sh start myapp 1.0.0

# Add BuildRequires and rebuild
specter.sh requires specter.sh-rust-myapp.spec -devel >> rust-myapp.spec
rpmbuild -ba rust-myapp.spec
```

### Handling Missing Dependencies

Some dependencies might not exist in Fedora yet. You'll need to build them first:

```bash
# Create directory structure for missing package
mkdir -p ~/dev/redhat/pkgs/rpm-rust-foo/rpms/foo
cd ~/dev/redhat/pkgs/rpm-rust-foo/rpms/foo

# Repeat the workflow for the dependency
rust2rpm foo 0.1.5
specter.sh getcrate foo 0.1.5
specter.sh init rust-foo.spec
specter search -i specter.sh-rust-foo.spec -b f38 -o foo-deps.json
specter requires -i foo-deps.json -p -c
# ... update spec, build again
```

### Track Progress with README (Bash - not yet in Python)

Use the template system to generate README files tracking your dependency tree:

```bash
cd ~/dev/redhat/pkgs/rpm-rust-myapp/rpms/myapp
python3 ~/dev/gen/specter/scripts/specrender.py \
    --name myapp \
    --ver 1.0.0 \
    --dest README.md \
    foo bar
```

This creates a README with checkboxes to track build progress.

## Understanding the Output

### JSON Structure

The `specter search` command produces JSON like this:

```json
[
  {
    "name": "(crate(foo/default)",
    "minsig": ">=",
    "minver": "0.1.0",
    "maxsig": "<",
    "maxver": "0.2.0",
    "rpm_name": "rust-foo+default-devel",
    "avaver": "0.1.5",
    "status": "FOUND"
  },
  {
    "name": "(crate(bar/feature)",
    "minsig": ">=",
    "minver": "1.5.0",
    "maxsig": "<",
    "maxver": "2.0.0",
    "rpm_name": "rust-bar+feature-devel",
    "avaver": "Not Found",
    "status": "NOT"
  }
]
```

### Status Values

- **FOUND**: Package exists in Fedora repos with compatible version
- **NOT**: Package not found in Fedora repos (needs to be built)
- **MISS**: Package exists but version doesn't satisfy requirements

## Package Name Conversion

Specter automatically converts crate syntax to Fedora package naming:

| Crate Name | Fedora Package Name |
|-----------|-------------------|
| `crate(foo/default)` | `rust-foo+default-devel` |
| `crate(bar/feature)` | `rust-bar+feature-devel` |
| `crate(baz-quux/std)` | `rust-baz-quux+std-devel` |

### Versioned Packages

When multiple major versions exist, Fedora uses version suffixes:

| Version | Package Name |
|---------|-------------|
| 0.x.x | `rust-foo+default-devel` or `rust-foo0+default-devel` |
| 1.x.x | `rust-foo1+default-devel` |
| 2.x.x | `rust-foo2+default-devel` |

The `specter search` command automatically tries versioned variants if the base package isn't found or has version mismatches.

## Integration with Fedora Tools

### mdapi - Fedora Metadata API

Python `specter search` queries mdapi to check package availability:
```
https://mdapi.fedoraproject.org/f38/pkg/rust-foo+default-devel
```

Supports all Fedora branches: `f38`, `f39`, `f40`, `rawhide`, etc.

### rust2rpm - Spec Generation

Generate initial spec files:
```bash
rust2rpm mypackage 1.0.0
```

Specter complements rust2rpm by handling the BuildRequires discovery.

### Fedora Rust Packaging Guidelines

Specter automates many requirements from the [Fedora Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/):

- **Package naming**: Follows `rust-$crate+$feature-devel` format
- **BuildRequires**: Generates proper version constraints
- **Version handling**: Supports both range and exact version matching

## Examples

### Example 1: Simple Package (Recommended Workflow)

```bash
# 1. Generate spec and download
rust2rpm defmac 0.2.1
specter.sh getcrate defmac 0.2.1

# 2. Capture dependencies (bash)
specter.sh init rust-defmac.spec

# 3. Search (Python - better!)
specter search -i specter.sh-rust-defmac.spec -b f38 -o defmac.json

# 4. Generate and apply BuildRequires (Python - better!)
specter requires -i defmac.json -c
vim rust-defmac.spec  # paste from clipboard

# 5. Install deps and build
sudo dnf builddep rust-defmac.spec
rpmbuild -ba rust-defmac.spec
```

### Example 2: Simple Package (Pure Bash)

```bash
# One command automation (uses bash search with dnf)
specter.sh start defmac 0.2.1

# Add BuildRequires and build
specter.sh requires specter.sh-rust-defmac.spec -devel >> rust-defmac.spec
rpmbuild -ba rust-defmac.spec
```

### Example 3: Complex Package (chariott)

The chariott package demonstrates handling 100+ dependencies:

```bash
# 1. Setup
rust2rpm chariott 0.1.0
specter.sh getcrate chariott 0.1.0

# 2. Capture dependencies (bash)
specter.sh init rust-chariott.spec

# 3. Search dependencies (Python - better!)
specter search -i specter.sh-rust-chariott.spec -b f38 -o chariott.json

# 4. List what's missing (Python)
specter requires -i chariott.json -l

# Output shows many are missing - need to build them first:
# - rust-criterion (and its 20+ deps)
# - rust-prost (needs version bump)
# - rust-tensorflow (and its 15+ deps)
# - rust-tonic (and its 25+ deps)
# - rust-bollard (and its 10+ deps)
# - rust-ndarray
# - rust-metrics-util
```

See the full dependency tree: `/home/ibrandao/dev/redhat/pkgs/rpm-rust-chariott/rpms/chariott/README.md`

## Troubleshooting

### Package Not Found

**Problem:** `specter search` shows status `NOT` for a package.

**Solution:** The package doesn't exist in Fedora repos yet. You'll need to build it yourself:
1. Use `specter.sh getcrate <package> <version>` to download the crate
2. Follow the workflow above to create the package
3. Build to Copr or local repo
4. Add the repo and retry

### Version Mismatch

**Problem:** `specter search` shows status `MISS` - package exists but wrong version.

**Solution:**
- The search automatically tries versioned packages (e.g., `rust-foo2+default-devel`)
- Check if a different version works
- Consider bumping the package version in Fedora
- Modify your spec to accept available versions (if compatible)

### mdapi Timeout

**Problem:** `specter search` hangs or times out.

**Solution:**
- mdapi can be slow or down - retry later
- Use `-l` flag to just list dependencies without searching:
  ```bash
  specter search -i specter.sh-rust-foo.spec -l
  ```
- Search specific packages manually with `dnf search`

### Clipboard Not Working

**Problem:** `specter requires -c` doesn't copy to clipboard.

**Solution:**
- Install pyperclip dependencies for your platform
- On Linux, ensure `xsel` or `xclip` is installed:
  ```bash
  sudo dnf install xsel
  ```
- Alternatively, use `-p` to print and copy manually

### Wrong File Format

**Problem:** `specter search` can't parse the input file.

**Solution:**
- Make sure you're using the file created by `specter.sh init`
- The file should be named `specter.sh-rust-*.spec`
- The file should contain lines like: `(crate(foo/default) >= 0.1.0 with...`
- Check the file exists: `ls -la specter.sh-rust-*.spec`

## Migration Status

Specter is being migrated from bash to Python for better functionality.

### Completed (Use Python)

| Feature | Python Command | Why Better |
|---------|---------------|------------|
| Parse dependencies | `specter search` | Robust Python parsing vs sed/awk |
| Search packages | `specter search` | mdapi API vs dnf commands (faster) |
| Version comparison | `specter search` | `packaging` library vs string comparison (accurate) |
| Generate BuildRequires | `specter requires` | JSON input, rich formatting, clipboard |

### Not Yet Migrated (Use Bash)

| Feature | Bash Command | Status |
|---------|-------------|--------|
| Download crates | `specter.sh getcrate` | Planned for Python |
| Capture errors | `specter.sh init` | Planned for Python |
| Complete automation | `specter.sh start` | Planned for Python |
| Copr integration | `specter.sh copr` | Planned for Python |
| README generation | `specrender.py` | Planned for Python |

### Why Python Is Better

**Python advantages:**
- Uses mdapi API (faster than dnf commands)
- Accurate version comparison with `packaging` library (not string comparison)
- Rich formatted output with tables and colors
- JSON output for automation
- Cross-platform clipboard support
- More maintainable and testable code

**Bash limitations:**
- String-based version comparison (fails on 0.9.0 vs 0.10.0)
- Slower dnf commands instead of API calls
- Fragile sed/awk parsing
- Linux-only

## Future Roadmap

### Complete Python Migration

Remaining features to migrate:
- [TODO] Crate downloading (`specter getcrate`)
- [TODO] Error capture (may not be needed, can parse rpmbuild output directly)
- [TODO] Complete automation workflow (`specter start`)
- [TODO] Copr integration (`specter copr`)
- [TODO] README generation from templates

### Multi-Language Support

#### Python Package Support
```bash
# Future syntax
specter search -i build-errors.txt -b f38 --ecosystem python
# Convert: pkg-foo >= 1.0 → python3-pkg-foo >= 1.0
```

#### Go Module Support
```bash
# Future syntax
specter search -i build-errors.txt -b f38 --ecosystem go
# Convert: github.com/foo/bar v1.2.3 → golang-github-foo-bar-devel
```

### Generic Dependency Framework
- Abstract the dependency resolution logic
- Plugin system for language ecosystems
- Common mdapi/DNF interface
- Universal template system

## See Also

- [Bash Scripts Documentation](scripts/README.md) - Complete bash command reference and raw workflow details
- [Fedora Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/)
- [rust2rpm Documentation](https://pagure.io/fedora-rust/rust2rpm)
- [mdapi API Documentation](https://mdapi.fedoraproject.org/)
- [Fedora Copr](https://copr.fedorainfracloud.org/)

## License

See LICENSE file for details.
