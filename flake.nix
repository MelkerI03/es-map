{
  description = "A Nix-flake-based Python project";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs {
              inherit system;
              config.allowUnfree = true;
            };
          }
        );

      version = "3.13";

      concatMajorMinor =
        pkgs: v:
        pkgs.lib.pipe v [
          pkgs.lib.versions.splitVersion
          (pkgs.lib.sublist 0 2)
          pkgs.lib.concatStrings
        ];
    in
    {

      ######################################################################
      # Package
      ######################################################################

      packages = forEachSupportedSystem (
        { pkgs }:
        let
          python = pkgs."python${concatMajorMinor pkgs version}";
        in
        {
          default = python.pkgs.buildPythonApplication {
            pname = "my-app";
            version = "0.1.0";

            src = ./.;

            pyproject = true;

            # Runtime dependencies go here
            propagatedBuildInputs = with python.pkgs; [
              graphviz
            ];

            doCheck = false; # As long as there arent any.
          };
        }
      );

      ######################################################################
      # DevShell
      ######################################################################

      devShells = forEachSupportedSystem (
        { pkgs }:
        let
          python = pkgs."python${concatMajorMinor pkgs version}";
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python
              python.pkgs.pip
              graphviz
            ];
          };
        }
      );
    };
}
