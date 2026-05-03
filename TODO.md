# fix
- after fragmentation, the fragments from the large object's side must be more attracted to it (it can be achieved by adding some acceleration towards that direction)
- upon collision, the fragments must go to different sides: the objects at the collided side must go further and hit the object in front of them (they can merge then), and other must go forward-left and forward-right (depending on where they are from the collision point).

# check

# feat
- lock view at one object
- lock view at several objects

# notes
- Now when the Moon and the Earth are static and the step of the simulation is 1 second, they unite upon collision.
- !!!!! In collision simulation, the objects break into fragments and those fragments perfectly go to each other instead of flying to different sides.

# results
## good simulations
- [x] Earth and Moon
- [x] three objects
