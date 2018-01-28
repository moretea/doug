{ pkgs ? (import <nixpkgs> {}) }:
with pkgs;
{
  doug = pkgs.python3.pkgs.buildPythonPackage rec {
    name = "doug";
    propagatedBuildInputs = with pkgs; [python3Packages.pygobject3];
    src = ./.;

    doCheck = false;

    meta = {
      homepage = "https://github.com/moretea/doug";
      description = "Doug hypernote editor";
      license = lib.licenses.gpl3;
    };
  };
}
