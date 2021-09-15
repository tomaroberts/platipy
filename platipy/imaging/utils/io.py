from matplotlib import cm
import numpy as np
import SimpleITK as sitk

import matplotlib.colors as mcolors


def write_nrrd_structure_set(
    masks,
    output_file="structure_set.nrrd",
    colormap=cm.get_cmap("rainbow"),
):
    """Write an nrrd structure given a set of masks. Useful for reading in Slicer.

    Args:
        masks (dict): Key is structure name, value is SimpleITK.Image
        output_file (str, optional): The path to write the nrrd file. Defaults to
            "structure_set.nrrd".
        colormap (matplotlib.colors.Colormap | dict, optional): Colormap to use for output.
            Can also use a dictionary with keys as structure names and values as colors.
            Defaults to cm.get_cmap("rainbow").

    Raises:
        AttributeError: masks must be a dict
        ValueError: colormap must be a matplotlib colormap or a dictionary
    """

    if not isinstance(masks, dict):
        raise AttributeError("masks should be dict with key name and value SimpleITK.Image")

    all_arr = np.zeros(0)
    structure_count = 1
    structure_names = []
    structure_values = []
    structure_layers = []

    for structure_name in masks:
        mask = masks[structure_name]

        arr = sitk.GetArrayFromImage(mask)
        if not len(np.unique(arr)) == 2:
            continue

        arr = arr[:, :, :, np.newaxis]

        structure_value = 1
        dim = 0
        if len(all_arr) > 0:

            # Check if this structure has space in the current dim
            # Append a new dim if not
            struct_added = False
            for dim in range(all_arr.shape[3]):
                if np.count_nonzero(all_arr[:, :, :, dim][arr[:, :, :, 0] > 0]) > 0:
                    # Overlap! look at next dim
                    continue

                structure_value = np.max(all_arr[:, :, :, dim]) + 1
                all_arr[:, :, :, dim] = all_arr[:, :, :, dim] + (
                    arr[:, :, :, 0] * (structure_value)
                )
                struct_added = True
                break

            if not struct_added:
                all_arr = np.concatenate((all_arr, arr), axis=3)
                dim += 1
        else:
            all_arr = arr

        structure_names.append(structure_name)
        structure_values.append(structure_value)
        structure_layers.append(dim)
        structure_count += 1

    struct_im = sitk.GetImageFromArray(all_arr)
    struct_im.SetSpacing(mask.GetSpacing())
    struct_im.SetOrigin(mask.GetOrigin())
    struct_im.SetDirection(mask.GetDirection())
    extent = (
        f"0 {struct_im.GetSize()[0]-1} 0 {struct_im.GetSize()[1]-1} 0 {struct_im.GetSize()[2]-1}"
    )

    structure_count = 0

    for name in structure_names:
        if isinstance(colormap, (mcolors.ListedColormap, mcolors.LinearSegmentedColormap)):
            color = colormap(hash(name) % 256)
        elif isinstance(colormap, dict):
            color = colormap[name]
        else:
            raise ValueError("colormap must be either a matplotlib colormap or a dictionary!")

        color = color[:3]
        color = [str(c) for c in color]

        struct_im.SetMetaData("Segment{0}_Color".format(structure_count), " ".join(color))
        struct_im.SetMetaData("Segment{0}_ColorAutoGenerated".format(structure_count), "1")
        struct_im.SetMetaData("Segment{0}_Extent".format(structure_count), extent)
        struct_im.SetMetaData(
            "Segment{0}_ID".format(structure_count), f"Segment_{structure_count+1}"
        )
        struct_im.SetMetaData(
            "Segment{0}_LabelValue".format(structure_count),
            str(structure_values[structure_count]),
        )
        struct_im.SetMetaData(
            "Segment{0}_Layer".format(structure_count), str(structure_layers[structure_count])
        )
        struct_im.SetMetaData("Segment{0}_Name".format(structure_count), str(name))
        struct_im.SetMetaData("Segment{0}_NameAutoGenerated".format(structure_count), "1")
        struct_im.SetMetaData("Segment{0}_Tags".format(structure_count), "")

        structure_count += 1

    sitk.WriteImage(struct_im, str(output_file))
