{
    description = "Python Java Poet Development Environment";

    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        nixpkgs-stable.url = "github:nixos/nixpkgs/release-24.11";

        pyproject-nix = {
        url = "github:pyproject-nix/pyproject.nix";
        inputs.nixpkgs.follows = "nixpkgs";
        };

        uv2nix = {
        url = "github:pyproject-nix/uv2nix";
        inputs.pyproject-nix.follows = "pyproject-nix";
        inputs.nixpkgs.follows = "nixpkgs";
        };

        pyproject-build-systems = {
        url = "github:pyproject-nix/build-system-pkgs";
        inputs.pyproject-nix.follows = "pyproject-nix";
        inputs.uv2nix.follows = "uv2nix";
        inputs.nixpkgs.follows = "nixpkgs";
        };
    };

  outputs = { self, nixpkgs, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      nixpkgsFor = forAllSystems (system:
        import nixpkgs {
          inherit system;
        }
      );
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
          python = pkgs.python312;

          # Load uv workspace
          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          # Create overlay from workspace
          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          # Editable overlay for local development
          editableOverlay = workspace.mkEditablePyprojectOverlay {
            root = "$REPO_ROOT";
            members = [ "python-java-poet" ];
          };

          pythonSetDev =
            (pkgs.callPackage pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                pkgs.lib.composeManyExtensions [
                  pyproject-build-systems.overlays.default
                  overlay
                  editableOverlay
                ]
              );

          venv = pythonSetDev.mkVirtualEnv ".venv" workspace.deps.default;
        in
        {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.uv
              venv
            ];

            env = {
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = python.interpreter;
            };

            shellHook = ''
              unset PYTHONPATH

              # Set REPO_ROOT to current directory if not already set
              export REPO_ROOT="''${REPO_ROOT:-$(pwd)}"

              # Activate the virtual environment from nix
              if [[ -f ${venv}/bin/activate ]]; then
                source ${venv}/bin/activate
              fi
            '';
          };
        }
      );
    };
}