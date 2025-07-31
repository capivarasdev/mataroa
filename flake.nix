{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    devenv.url = "github:cachix/devenv";
  };

  outputs = { self, nixpkgs, devenv, ... } @ inputs:
    let
      forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed;
    in
    {
      packages = forAllSystems (system: {
        devenv-up = self.devShells.${system}.default.config.procfileScript;
      });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules = [
              ({ pkgs, ... }: {
                services.postgres = {
                  enable = true;
                  initialDatabases = [
                    {
                      name = "mataroa";
                      user = "postgres";
                    }
                  ];
                  listen_addresses = "localhost";
                  initialScript = ''
                    CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';
                  '';
                };

                languages.python = {
                  enable = true;
                  uv.enable = true;
                  uv.sync.enable = true;
                };
              })
            ];
          };
        });
    };
}
