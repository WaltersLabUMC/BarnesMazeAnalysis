# Barnes Maze Analysis

## About

Python script that takes xy-coordinate data from DeepLabCut projects (https://github.com/deeplabcut/deeplabcut) and performs various Barnes Maze-related behavioral analyses. 

## Highlights

1. bulk processing of xy-coordinate files
2. all bodypart labels are analyzed
3. optional quadrant analysis
4. optional dynamic velocity (velocity measured in one second bins)
5. user-friendly Jupyter lab notebook template and extensive usage documentation

### Output metrics 

- total distance traveled
- mean velocity and optional dynamic velocity (velocity measured in one second bins)
- latency to first visit for each hole and/or quadrant
- total time spent in each hole and/or quadrant's entry zone
- total number of visits to each hole and/or quadrant

## Installation 

```
git clone https://github.com/WaltersLabUMC/BarnesMazeAnalysis.git
cd BarnesMazeAnalysis
```

See the following documents in the GitHub for detailed user guides:

- [Jupyter notebook template](https://github.com/WaltersLabUMC/BarnesMazeAnalysis/blob/main/Jupyter_notebook_template.ipynb)
- [Quickstart guide](https://github.com/WaltersLabUMC/BarnesMazeAnalysis/blob/main/Quickstart_guide.pdf)
- [Function Reference documentation](https://github.com/WaltersLabUMC/BarnesMazeAnalysis/blob/main/Function_reference_documentation.pdf)

## Authors
- Kendra L. Stansak (https://orcid.org/0009-0008-2756-8030): DeepLabCut model optimization, pipeline development, validation, and documentation
- Luke D. Baum (https://github.com/LukeBaum): pipeline development
- Bradley J. Walters: principal investigator, project supervision

Developed in the Walters Lab, University of Mississippi Medical Center.

## How to Cite

If you use BarnesMazeAnalysis in your research, please cite:

Stansak KL, Baum, LD, Walters BJ. BarnesMazeAnalysis: Python pipeline for extracting Barnes maze metrics from DeepLabCut tracking data. Version 1.0.0. GitHub; 2026. https://github.com/WaltersLabUMC/BarnesMazeAnalysis

Please also cite DeepLabCut:

Mathis A, Mamidanna P, Cury KM, Abe T, Murthy VN, Mathis MW, Bethge M. DeepLabCut: markerless pose estimation of user-defined body parts with deep learning. Nature Neuroscience. 2018;21:1281–1289.


## License

Please read the License document provided. BarnesMazeAnalysis is intended for use in research and the creators request to be cited in any resulting publications.
