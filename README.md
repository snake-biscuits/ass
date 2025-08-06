# ass

**A**bstract **S**olids & **S**cenes
Python Library for handling 3D *ass*ets

Not to be confused with [assimp](https://github.com/assimp/assimp/)

## Features
### Migrating
 - [ ] `bsp_tool.utils.geometry`
 - [ ] `bsp_tool.utils.physics`
 - [ ] `bsp_tool.scene`

### Planned
 * `Material` update
   - Shader Languages (OSL, GLSL, HLSL)
   - Node Graphs (Blender, GlTF, USD)
 * `bite.Material` support
   - `bite` should extend `ass` w/ parsed file formats
 * pip extras
   - `openusd`
     * `pixar.Usd.from_file`
   - `bpy`
     * `Material` -> Nodes
     * `Model` -> Object & bmesh
 * `khronos.Dae` (`model/vnd.collada+xml`)
   - Originally created at Sony Computer Entertainment
   - COLLADA DOM uses SCEA Shared Source License 1.0
   - Wikipedia page is a good reference
 * `blockbench.Model`
   - or `ass.BBModel`
   - `import blockbench.Model as BBModel`
 * pip extras
   - `viewer` (same dependencies as `usdview`)


## Installation

> TODO: how to get ass


## Usage

> TODO: how to use ass
