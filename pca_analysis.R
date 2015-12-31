source('loading_plot.R')

run_pca_analysis <- function(csv_file, variables, components)
{
    # Load data
    elite <- read.csv(csv_file)
    st <- elite[, 'st']
    m <- elite[, variables]

    m.pca <- prcomp(m, center=TRUE, scale.=TRUE)
    print(m.pca)
    print(summary(m.pca))


    g <- loading_plot(m.pca, choices=components, circle=TRUE, ellipse=FALSE, points=FALSE,
            alpha=0.3, groups=st, varname.size=5, varname.adjust = 1.5)
    g <- g + scale_color_discrete(name = '')
    g <- g + theme(legend.direction = 'horizontal',
                   legend.position = 'top')
    print(g)

    # Save to pdf
    output_file <- paste('output/loading_plot_', components[1], 'x', components[2], '.pdf', sep='')
    dev.copy(pdf, file=output_file)
    dev.off()
}