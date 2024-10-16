# MDTraj NumPy 2 Upgrade - Comparison of LAMMPSTrajectory Behavior

When upgrading MDTraj to NumPy 2.0, it is observed that seven tests in the test suite fail.
This repository is an investigation of the behavior surrounding one of those tests.
The test can be found [here](https://github.com/mdtraj/mdtraj/blob/b4447a1a6e8e9899bafec4d7ffb8bdce5d41aa60/tests/test_lammpstrj.py#L58).

In this test, one NumPy array representing lengths is created and another NumPy array representing angles is created.
These two arrays are passed to the `LAMMPSTrajectory` class, which creates a lammps trajectory file.
The created file is then read in and the lengths and angles are compared to the original arrays.

The tests pass with NumPy 1.x, but fail with NumPy 2.0.

In order to figure out how to fix this test, we have to understand why the test is failing with NumPy 2.0. Is it because of a change with the output arrays, or is it a change with the way comparisons are done? If we are looking to **maintain** behavior of MDTraj, we will have to figure out which of these is happening and how to fix it.

## Overview of the Failing Test

The test in question can be found [here](https://github.com/mdtraj/mdtraj/blob/b4447a1a6e8e9899bafec4d7ffb8bdce5d41aa60/tests/test_lammpstrj.py#L58). It generates random arrays representing `xyz` coordinates, `lengths`, and `angles` of a trajectory. The [`LAMMPSTrajectory` class](https://github.com/mdtraj/mdtraj/blob/b4447a1a6e8e9899bafec4d7ffb8bdce5d41aa60/mdtraj/formats/lammpstrj.py#L123) writes these arrays to a file and then reads them back, and the original and written arrays are compared.

The test code is as follows:

```python
def test_read_write_0():
    xyz = 10 * np.random.randn(100, 11, 3)
    lengths = np.ones(shape=(100, 3))
    angles = np.empty(shape=(100, 3))
    angles.fill(45)

    with LAMMPSTrajectoryFile(temp, mode="w") as f:
        f.write(xyz, lengths, angles)
    with LAMMPSTrajectoryFile(temp) as f:
        xyz2, new_lengths, new_angles = f.read()

    eq(lengths, new_lengths)
    eq(angles, new_angles)
    eq(xyz, xyz2, decimal=3)
```
In this test, arrays for xyz, lengths, and angles are passed to the LAMMPSTrajectory class, which writes them to a file. The test compares the original arrays with the ones read from the file.

The test passes with NumPy 1.x, but fails with NumPy 2.0.

## Modified Test for Investigation

I modified the test to save new and original arrays using pickle. The modified test is as follows:

```python
def test_read_write_0():

    np.random.seed(1)

    xyz = 10 * np.random.randn(100, 11, 3)
    lengths = np.ones(shape=(100, 3))
    angles = np.empty(shape=(100, 3), dtype=np.float64)
    angles.fill(45)

    with LAMMPSTrajectoryFile(temp, mode="w") as f:
        f.write(xyz, lengths, angles)
    with LAMMPSTrajectoryFile("reference.lammpstrj", mode="w") as f:
        f.write(xyz, lengths, angles)
    with LAMMPSTrajectoryFile(temp) as f:
        xyz2, new_lengths, new_angles = f.read()

    # save new angles and lengths using pickle
    import pickle

    with open("np2_new.pkl", "wb") as f:
        pickle.dump((xyz2, new_lengths, new_angles), f)
    
    # save original angles and lengths using pickle
    with open("np2_original.pkl", "wb") as f:
        pickle.dump((xyz, lengths, angles), f)

    #assert angles.dtype == new_angles.dtype
    eq(lengths, new_lengths)
    eq(angles, new_angles)
    eq(xyz, xyz2, decimal=3)
```

I ran this test using NumPy 1.x and NumPy 2.0. The output arrays were saved using pickle.

Then, I changed the datatype in LAMMPSTrajectory to `np.float64` and ran the test again using NumPy 2.0.

The arrays were compared in the notebook `comparison.ipynb`

## Results

I subracted the original arrays from the new arrays and calculated the maximum difference for each array. The results are as follows:

```
np1 (NumPy 1.0) - Max difference for tuple 1 (xyz): 0.000499959303509101
np1 (NumPy 1.0) - Max difference for tuple 2 (lengths): 6.661338147750939e-16
np1 (NumPy 1.0) - Max difference for tuple 3 (angles): 9.805755212255463e-07
np2 (NumPy 2.0) - Max difference for tuple 1: 0.000499959303509101
np2 (NumPy 2.0) - Max difference for tuple 2: 5.307949098032338e-07
np2 (NumPy 2.0) - Max difference for tuple 3: 3.1392858353740394e-05
np2_np64 (NumPy 2.0 with np64) - Max difference for tuple 1: 0.000499959303509101
np2_np64 (NumPy 2.0 with np64) - Max difference for tuple 2: 9.992007221626409e-16
np2_np64 (NumPy 2.0 with np64) - Max difference for tuple 3: 5.684341886080802e-14
```

When upgrading to NumPy 2.0, it appears that some precision is lost, particularly in lengths and angles. 
Array values are *closest* to the original input value with NumPy 2.0 and `np.float64` used in `LAMMPSTrajectory`.