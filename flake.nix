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
            pname = "es-map";
            version = "0.1.0";

            src = ./.;

            pyproject = true;

            nativeBuildInputs = with python.pkgs; [
              setuptools
              wheel
            ];

            # Runtime dependencies go here
            propagatedBuildInputs = with python.pkgs; [
              graphviz
              elasticsearch
              python-dotenv
              typer
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
              python.pkgs.graphviz
              python.pkgs.python-dotenv
              python.pkgs.typer
              python.pkgs.elasticsearch

              graphviz
              # elasticsearch
            ];
          };
        }
      );
    };
}
