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

- Jupyter notebook template
- Quickstart guide
- Function Reference documentation

## License

Please read the License document provided. BarnesMazeAnalysis is intended for use in research and the creators request to be cited in any resulting publications.
