# fix
 
- add a button which enables / disables our coefficients for artificial changes of the bodies characteristics such as impulses upon collision etc.
  I think it can be done just by changing the coefficients if the user turns that parameter on/off, like it just won't affect anything this way

- when body destructs, its fragments are too small in radius. they must be larger and also their radius must depend on their count and the radius of parent object.

# check

# feat
- add more real-life objects
  - the user must be able to add not only custom objects, but also rocky objects from real life within our value ranges (Mercury, Venus, Earth, Mars)
  - these preset planets must be able to be chosen when the user is adding a new object into the simulation
- toggle displaying objects names

## later
- lock view at one object
- lock view at several objects
- lock scale when it enlarged (for some time, so that it is not constantly zooming in and out)

# notes
- Now when the Moon and the Earth are static and the step of the simulation is 1 second, they unite upon collision.
- !!!!! In collision simulation, the objects break into fragments and those fragments perfectly go to each other instead of flying to different sides.

# results
## good simulations
- [x] Earth and Moon
- [x] three objects
