{
  description = "A Nix-flake-based Python project";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
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
      ###########
      # Package #
      ###########

      packages = forEachSupportedSystem (
        { pkgs }:
        let
          python = pkgs."python${concatMajorMinor pkgs version}";
          py = python.withPackages (p: [
            p.networkx
            p.elasticsearch
            p.python-dotenv
            p.typer
            p.pygraphviz
          ]);

          commonInputs = [
            py
            python.pkgs.nuitka
            pkgs.graphviz
          ];

          makeNuitkaDerivation =
            buildType:
            pkgs.stdenv.mkDerivation {
              pname = "es-map-${buildType}";
              version = "0.1.0";
              src = ./.;

              nativeBuildInputs = [
                py
                pkgs.graphviz
              ];

              buildInputs = commonInputs;

              buildPhase = ''
                mkdir -p build

                nuitka \
                  --follow-imports \
                  --show-progress \
                  --output-dir=build \
                  --output-filename=es-map \
                  ${pkgs.lib.optionalString (buildType == "release") "--onefile --lto=yes"} \
                  es_map/cli.py
              '';

              installPhase = ''
                mkdir -p $out/bin
                cp build/es-map* $out/bin/es-map
              '';

              doCheck = false;
            };
        in
        {
          dev = makeNuitkaDerivation "dev";
          release = makeNuitkaDerivation "release";

          default = python.pkgs.buildPythonApplication {
            pname = "es-map";
            version = "0.1.0";

            src = ./.;

            pyproject = true;

            nativeBuildInputs = with python.pkgs; [
              setuptools
              wheel
            ];

            propagatedBuildInputs = with python.pkgs; [
              networkx
              elasticsearch
              python-dotenv
              typer
              pygraphviz
            ];

            doCheck = false;
          };

          windows = pkgs.stdenv.mkDerivation {
            pname = "es-map-win";
            version = "0.1.0";
            src = ./.;

            nativeBuildInputs = [
              py
              pkgs.graphviz
            ];

            buildInputs = commonInputs;

            buildPhase = ''
              mkdir -p build

              nuitka \
                --follow-imports \
                --show-progress \
                --output-dir=build \
                --output-filename=es-map.exe \
                --onefile \
                --lto=yes \
                es_map/cli.py
            '';

            installPhase = ''
              mkdir -p $out/bin
              cp build/es-map.exe $out/bin/es-map.exe
            '';

            doCheck = false;
          };
        }
      );

      ############
      # DevShell #
      ############

      devShells = forEachSupportedSystem (
        { pkgs }:
        let
          python = pkgs."python${concatMajorMinor pkgs version}";
        in
        {
          default = pkgs.mkShell {
            packages = with python.pkgs; [
              python
              pip
              graphviz
              python-dotenv
              typer
              elasticsearch
              networkx
              pygraphviz

              pkgs.graphviz
              # pkgs.elasticsearch
            ];
          };
        }
      );
    };
}
