# ass

**A**bstract **S**olids & **S**cenes

Python Library for handling 3D *ass*ets

Not to be confused with [assimp](https://github.com/assimp/assimp/)


## Features
### Solids
 * `physics`
   - `AABB`
   - `Brush`
   - `Plane`
 * `vector`
   - `vec2`
   - `vec3`
 * `quaternion.Quaternion`

### Scenes
File format parsers for 3D models

| extension | parser | MIME type | read | write |
| :--- | :--- | :--- | :--- | :--- |
| `*.bbmodel` | `blockbench.BBModel` | `text/json` | :-1: | :-1: |
| `*.dae` | `khronos.Dae` | `model/vnd.collada+xml` | :-1: | :-1: |
| `*.gltf` | `khronos.Gltf` | `model/gltf+json` | :-1: | :+1: |
| `*.glb` | `khronos.Gltf` | `model/gltf-binary` | :-1: | :-1: |
| `*.usd` | `pixar.Usd` | | | |
| `*.usda` | `pixar.Usd` | `model/vnd.usda` | :-1: | :+1: |
| `*.usdc` | `pixar.Usd` | | :-1: | :-1: |
| `*.usdz` | `pixar.Usd` | `model/vnd.usdz+zip` | | |
| `*.mdl` | `valve.Mdl` | | :+1: | :-1: |
| `*.obj` | `wavefront.Obj` | `model/obj` | :+1: | :+1: |

> `*.usd` extension can be used for either `*.usda` or `*.usdc`

> `*.usdz` can be opened with `pixar.Usd.from_archive`

> `*.mdl` support is currently only for v53 (Titanfall 2)

> `blockbench.BBModel` & `khronos.Dae` are planned


## Installation

<!-- how to get ass -->

To use the
latest **unstable** version, clone with `git`:
```
$ git clone git@github.com:snake-biscuits/ass.git
$ cd ass
$ pip install -e .
```

You can also clone with `pip`:

```
$ pip install git+https://github.com/snake-biscuits/ass.git
```

Or, use the latest **stable** release (August 2026 | 0.1.0 | Python 3.8-14):
```
$ pip install ass
```


## Usage

> TODO: how to use ass
