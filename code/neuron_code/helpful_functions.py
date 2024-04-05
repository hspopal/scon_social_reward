try:
    import os
    from matplotlib.gridspec import GridSpec

    # Import cerebellum packages
    import matplotlib.pyplot as plt
    import SUITPy.flatmap as flatmap

    from nilearn.plotting import plot_stat_map
except ImportError:
    pass

def plot_transparent_threshold(filename, thresh=1, mc='fdr', mc_alpha=0.05, clust_alpha=0.05, view='split', title=''):
    # Find stat map
    stat_filename = os.path.join(filename+'_effect.nii.gz')
    stat_filename_mc = os.path.join(filename+'_zmap_'+mc+'-'+str(mc_alpha)+'.nii.gz')
    
    # Import stat map as a cerebellum flatmap
    funcdata = flatmap.vol_to_surf(stat_filename,
                                  space='SUIT')
    
    
    #mc_thresh = threshold_data[filename+'_zmap_'+mc+'-'+str(mc_alpha)]
    #print(mc_thresh)
    #if mc_thresh == np.inf:
    #    mc_thresh = 1000

    if view == 'split':
        # Set figure specs
        fig = plt.figure(figsize=(15, 6))
        gs = GridSpec(4, 2)

        # Plot whole brain maps
        ax_img1 = plt.subplot(gs[0, :])
        ax_img2 = plt.subplot(gs[1, :])
        
        hemi_lh = plot_stat_map(stat_filename, threshold=thresh, axes=ax_img1,
                                cut_coords=range(-65,0, 10), display_mode='x', colorbar=True,
                                cmap='coolwarm', symmetric_cbar=True, title='Left Hemisphere',
                                annotate=False)
        hemi_rh = plot_stat_map(stat_filename, threshold=thresh, axes=ax_img2,
                                cut_coords=range(66,5, -10), display_mode='x', colorbar=True,
                                cmap='coolwarm', symmetric_cbar=True, title='Right Hemisphere',
                                annotate=False)
        hemi_lh.add_contours(stat_filename_mc, levels=[-0.1,0.1], colors=['blue','red'], 
                          alpha=1, linewidths=1)
        hemi_rh.add_contours(stat_filename_mc, levels=[-0.1,0.1], colors=['blue','red'], 
                          alpha=1, linewidths=1)
        
        # Plot cerebellum flatmap
        ax_joint = plt.subplot(gs[2:, 0])
        ax_joint.set(title='Cerebellum flatmap')
        flatmap.plot(data=funcdata, cmap='coolwarm',
                    threshold=[-thresh,thresh],
                    colorbar=False,
                    render='matplotlib', new_figure=False)

        # Plot ventral striatum ROI
        ax_img3 = plt.subplot(gs[2:, 1])
        
        roi_map = plot_stat_map(stat_filename, threshold=thresh, axes=ax_img3,
                                cut_coords=[8], display_mode='y', colorbar=False,
                                cmap='coolwarm', symmetric_cbar=True, 
                                annotate=True)
        roi_map.add_contours(stat_filename_mc, levels=[-0.1,0.1], colors=['blue','red'], 
                          alpha=1, linewidths=1)
        
    elif view == 'straight':
        hemi_bh = plot_stat_map(stat_filename, threshold=thresh, 
                      cut_coords=range(-65,66, 10), display_mode='x', colorbar=True,
                      cmap='coolwarm', symmetric_cbar=True, title=title)
        hemi_bh.add_contours(stat_filename_mc, levels=[-0.1,0.1], colors=['blue','red'], 
                          alpha=1, linewidths=2)
