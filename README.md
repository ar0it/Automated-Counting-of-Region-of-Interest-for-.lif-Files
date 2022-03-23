# Automated-Counting-of-Region-of-Interest-for-.lif-Files
Contructs clusters of ROI and counts them. Implementation not computational efficient, but works fine because of numba.

HOW IT WORKS:
Normalizes the image, so that its min value is set to 0 while the previous max value is now 255. The data type chosen is
float64. Now every pixel of the image is looped through, the pixel will be checked for intensity by a threshold, 
that can be customized by changing the function "larger_than_threshold". If a pixel conforms with the threshold and
hasn't been added to the region of interest (roi) array, the pixel will be used as a starting point for a new pixel 
cluster. Growing the pixel cluster is done by checking all the neighbors of the previously mentioned pixel and adding
them to the que, so they can be checked if their intensity is in lign with the threshold as well. If that is the case,
they will be added to the cluster and their neighbors will be added to the que. This repeats until no new neighbors that
fulfill the threshold can be found. Now the process of lopping through the entire image will be repeated. Pixel that
were previously added to a cluster will be skipped. Finally the list of pixel clusters (so a list of lists) is obtained
the length of it responds to the number of cluster found. The clusters contain the indices and thus the position of all
the contained pixels in the image. This list of lists can now be further post processed by for example removing clusters
bellow a certain size.
