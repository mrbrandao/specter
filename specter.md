NAME: specter
DESCRIPTION:
    specter is a personification of a spec file.
    It works as a CLI command to simplify the RPM creation while dealing with the depencencies for build an RPM successfully.
    Real life problem example:
     - You are working to build a `rust` project from crates using rust2rpm. So the first you need the crates source package.
     In such situation when doing manually you might do those actions:

        * Download the Sources and create the spec file:
        
          Manual Solution:
           ```bash
            (cd $BUILD_ROOT/SOURCES/; curl -o foo.0.1.0.crates https://api.crates.io/download/foo.0.1.0.crates)
            rust2rpm foo 0.1.0
            ```

          Specter Solution:
            ```bash
             specter getcrate -p foo -v 0.1.0 -d $BUILD_ROOT/SOURCES/
             rust2rpm foo 0.1.0
            ```

        * Build the spec file:
          
            Manual Solution:
              ```bash
                rpmbuild -ba foo.spec
              ```
              _Since this will not have the BuildRequires it might fail asking to install the needed dependencies such as:_

              ```bash
              Error while building the dependencies:
                  (crate(bar/default) >= 0.1.0 with crate(bar/default) < 0.2.0~) is needed by foo-0.1.0.rpm
              ```
          Specter Solution:
           Specter helps to solve this by finding the crates dependencies and declaring it
           Example:
            ```bash
                specter generate -i foo.spec -o buildrequires.txt
                cat buildrequires.txt
                BuildRequires:  rust-bar+default-devel >= 0.1.0, rust-bar+default-devel < 0.2.0
            ```
            With this result you can easly update the `foo.spec` with this out put.

        * Install the dependencies:
            
            Problem:
            After declare the BuildRequires you might have this output when build:
            ```bash
               error: Failed build dependencies:
                    rust-bar+default-devel is needed by rust-foo+default-devel-1.fc38.x86_64 
            ```
            
            Manual Solution:
            ```bash
                dnf -y install rust-bar+default-devel
            ```
            _this action might be executed for each missing package_

            Specter Solution:
                ```bash
                    specter install -i buildrequires.txt # install all the package dependencies
                    specter search -i buildrequires.txt # search for the requirements
                    specter search -i buildrequires.txt -o install-list.txt # generate a list of packages found in the system
                ```
        *  Install the Missing packages:
            
            Problem:
                Some packages were not installed because they are missing in the distro, you might need to build them as well,
                those are called the subpackage dependencies.

            Manual Solution:
                ```bash
                    dnf -y search rust-bar|grep -E "rust-bar[?\+0-3]"
                    Found: rust-bar0.2+default-devel
                ```
                Fix the build requires:
                    ```
                        # vim foo.spec diff
                        ...
                        ...
                        +++ BuildRequires: rust-bar0.2+default-devel
                        --- BuildRequires: rust-bar+default-devel
                        ...
                        ...
                    ```
                ```bash
                    dnf -y install rust-bar0.2+default-devel
                ```

             Specter Soltion:
                ```bash
                    specter search -m -v "0-3" -i foo.spec -o mreq.txt # search specific package version and generate the file with the found BuildRequires 
                    specter install -m -i mreq.txt # install missing requirements
                ```
                
