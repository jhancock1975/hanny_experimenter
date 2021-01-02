### jsonlite for parsing json
### agricolae for Tukey HSD
### xtable for latex format ANOVA table
pacman::p_load(agricolae, gplots, multcompView, ggplot2, jsonlite, xtable, stringr, stringi)

get_data_for_n_factor_research_question <- function(file_name, factor_funcs,
                                                    factor_names){
### iterate through experiments in file_name
### decide factor from factor_func
### :param factor_name: goes in factor column of output dataframe
    
### parallel lists for dataframe to hold classifer and metrics
    factors <- matrix(nrow=0, ncol=length(factor_names))
    colnames(factors) <- factor_names
    auc <- c()
    f1 <- c()
    prec <- c()
    rec <- c()
    a_prc <- c()
    exp_names <- c()
    
### read file to nested list object
    document <- fromJSON(file_name)
    for (exp_name in names(document)){
### 10 iterations of 5-fold cross validation for
### every experiment
        cur_factors <- c()
        for (f in factor_funcs){
            cur_factors <- c(cur_factors, f(exp_name))
        }
        for (exp in document[[exp_name]]$results_data){
            for (iter in exp){
                factors <- rbind(factors, cur_factors)
                auc <- c(auc, iter$auc)
                f1 <- c(f1, iter$f1)
                prec <-c(prec, iter$precision)
                rec <- c(rec, iter$recall)
                a_prc <- c(a_prc, iter$a_prc)
            }
        }
    }
    res_df <- data.frame('auc'=auc, 'f1'=f1, 'prec'=prec, 'rec'=rec,
                         'a_prc'=a_prc)
### "factors" will have list of factors for each experiment
### so need to split lists into columns
    for (factor_name in factor_names){
        res_df[[factor_name]] = factors[, factor_name]
    }
    return(res_df)
}

proper_form <- function(s){
### formats things properly for report
    if (s == 'auc'){
        return('\\ac{AUC}')
    } else if (s == 'a_prc'){
        return('\\ac{AU PRC}')
    } else {
        return(s)
    }
}

escape_underscores <- function(s){
### latex requires us to escape underscores
    return(gsub('_', ' ', s))
}

remove_vector_constructor <- function(s){
### the gsub, gsub, gsub is to work around
### the way that the aggregated hsd groups (agg)
### are stored as strings of vectors like "c("LightGBM", ...)
### that we do not know how to deal with
    return (gsub("\\)", "",
                 gsub("\"", "",
                      gsub("c\\(\"", "", escape_underscores(s)))))
}

write_hsd_table <- function(aov_clf_metric, agg, metric, label, caption){
### code common to one and two factor anova/hsd
### for writing tables of groups
### param aov_clf_metric: analysis of variance results
### param ac analysis: configuration object
### param agg aggregated: hsd test results
### param label - latex label for table
### para caption - latex caption for table
### return string of latex code for a table
    end_row <- "\\\\ \\hline\n"
    result <- "\\bgroup\n"
    result <- paste(result, "\\begin{table}[H]\n")
    result <- paste(result, "\\centering\n")
    result <- paste(result, "\t\\begin{tabular}{l}\\hline\n")
    i <- 1
    for (level in agg[[1]]){
        result = paste(result, "\tGroup", level, "consists of:",
                      remove_vector_constructor(agg[[2]][i]),
                       end_row)
        i <- i+1
    }
    result = paste(result, "\t\\end{tabular}\n")
    result = paste0(result, "\t\\caption{", caption, "}\n")
    result = paste0(result, "\t\\label{tab:", label,  "}\n")
    result = paste(result, "\\end{table}")
    result = paste(result, "\\egroup")
    return(result)
}

englishify <- function(v){
### converts vector to english readable phrase
### for example c(1,2,3) -> 1, 2 and 3
### :param v: vector to be converted
    s <- stri_reverse(toString(v))
    s <- str_replace(s, ",", "dna ")
    return(stri_reverse(s))
}

make_level_dict <- function(agg){
### make a dictionary of factor names
### to numbers for coloring HSD plots
    i <- 1
    group_numbers <- c()
    level_names <-c()
    group_labels <- c()
    for (group_label in agg[[1]]) {
        for (group_members in agg[[2]][i]) {
            group_numbers <- c(rep(i, length(group_members)), group_numbers)
            group_labels <- c(rep(group_label, length(group_members)), group_labels)
            level_names <- c(group_members, level_names)
            }
        i <- i + 1
    }
    result <- data.frame(group_numbers = group_numbers,
                         level_names = level_names,
                         group_labels = group_labels)
    ii <- order(result$group_labels)
    return(result[ii,])
}
n_factor_research_question <- function(question_name, factors, metric, factor_funcs,
                                             input_file_name, output_file_name, make_boxplots = F){
### function to do ANOVA and HSD Test for n factors, no interaction
### :param question name: name of research question, usually Q1, Q2, etc.
### :param factors: list of treatment under anlysis
### :param metric: response analyized, for example area under precision recall curve
### :param factor_funcs: functions that returns level of factor, derived from experiment name
### in experiment results json file
### input_file_name: name of file containing experiment data, should be a file with a specific JSON
### format
### output_file_name: name of output latex file with experiment results
    write(
        paste("%statistical analysis of data from", input_file_name),
        file = output_file_name,
        append = T
    )
    
    write(
        paste0('Statistical analysis to answer research question \\textbf{', question_name,
              "}: Does ", englishify(factors), " impact performance in terms of ", proper_form(metric), "?"),
        file = output_file_name,
        append = T
    ) 
    
    df <- get_data_for_n_factor_research_question(input_file_name, factor_funcs, factors)


    factor_metric_model <- lm(paste(metric, "~", paste(factors, collapse=" + ")),
                              data=df)
    
    aov_factor_metric <- aov(factor_metric_model, data=df)
    aov_table <-xtable(aov_factor_metric, caption = paste("ANOVA for", englishify(factors),
                               "as factors of performance in terms of", proper_form(metric)
                               )
                       )
    aov_table_str <- print(aov_table, file = "/dev/null")
    aov_table_str <- sub("\\[ht\\]", "[H]", aov_table_str)
    write(aov_table_str, file = output_file_name, append = T)
    for (factor in factors){
        hsd_res <- HSD.test(aov_factor_metric, factor, alpha=0.01, console=F, group=T)
### print hsd groups for treatments/factors
        agg <- aggregate(rownames(hsd_res$groups) ~ hsd_res$groups$groups, hsd_res$groups, paste)
### make dictionary of factors to numbers for colors
        hsd_factor_dict <- make_level_dict(agg)
        write(write_hsd_table(aov_clf_metric, agg, metric,
                              paste0('hsd-', factor, '-', metric ),
                              paste('HSD test groupings after ANOVA of',
                                    proper_form(metric), 'with', factor, 'as a factor'
                                    )
                              ),
              file=output_file_name,
              append=T
              )
        if (make_boxplots == T) {
            plot_title <- paste(question_name, ": Mean", plotting_form(metric), "for levels of",
                                factor)
            png_file_name <- draw_boxplots(df[[metric]] ~ df[[factor]], df, factor,
                                           plotting_form(metric), 2, plot_title, hsd_factor_dict)
            fig <- "\n\\begin{figure}[H]\n"
            fig <- paste0(fig, "\t\\caption{Boxplots of mean ", proper_form(metric),
                          " for levels of ", factor)
            fig <- paste0(fig, "; HSD group printed below box; color corresponds to HSD group}\n")
            fig <- paste0(fig, "\t\\includegraphics[width=\\linewidth]{", png_file_name, "}\n")
            fig <- paste0(fig, "\t\\label{fig:", png_file_name, "}\n")
            fig <- paste0(fig, "\\end{figure}\n")
            write(fig, file = output_file_name, append = T)
        }
    }
}

plotting_form <- function(s){
### convert metric name to something suitable for plotting
    if (s ==  "auc"){
        return("AUC")
    } else if(s == "a_prc"){
        return("AU PRC")
    } else {
        return(s)
    }
}


## Transparent colors
## Mark Gardener 2015
## https://www.dataanalytics.org.uk/make-transparent-colors-in-r/

t_col <- function(color, percent = 50, name = NULL) {
                                        #      color = color name
                                        #    percent = % transparency
                                        #       name = an optional name for the color

    ## Get RGB values for named color
    rgb.val <- col2rgb(color)

    ## Make new color using input color as base and alpha set by transparency
    t.col <- rgb(rgb.val[1], rgb.val[2], rgb.val[3],
                 max = 255,
                 alpha = percent * 255 / 100,
                 names = name)

    return(t.col)
}

draw_boxplots <- function(f, x, xlab, ylab, las, main, hsd_factor_dict){
### generates box plots of experiment results per factor
### in the future we want  Tukey HSD groups on boxes
### return: name of file generated
    png_file_name <-   paste0(gsub(":", "-",
                                   gsub('_','-',
                                        gsub(',','',
                                             gsub(' ', '-',  tolower(main))))),
                              ".png")
    png( png_file_name )
    par(mar=c(10.5, 4.1, 4.1, 2.1))
    levels <- as.character(unique(x[[xlab]]))
    n_colors <- length(unique(hsd_factor_dict$group_labels))
    color_pallet <- unlist(lapply(rainbow(n_colors), function(x) t_col(x, 10)))
    color_list <- c()
    boxplot_label_list <- c()
    for (level in levels) {
        color_list <- c(color_pallet[
            subset(hsd_factor_dict, level_names == level)$group_numbers],
            color_list)
        boxplot_label_list <-
            c(as.vector(subset(hsd_factor_dict, level_names == level)$group_labels),
              boxplot_label_list)
    }


    bxp <- boxplot(f, data = x, las = las, xlab = "", ylab = ylab, main = main, col = color_list)

    level_colors <- c()
    for (i in unique(hsd_factor_dict$group_numbers)) {
        level_colors <- c(level_colors, color_pallet[i])
    }
    mtext(xlab, side = 1, line = 9)

    # draw hsd group number over box plots
    text(c(1 : length(hsd_factor_dict$level_names)) , bxp$stats[3, ] + 0.01,
                 boxplot_label_list)
    dev.off()
    return(png_file_name)
}
