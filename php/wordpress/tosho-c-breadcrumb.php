<?php
/**
 * Component: Breadcrumb Navigation
 * File: tosho-c-breadcrumb.php
 */

// Define the dynamic "TOP" text based on the provided logic
$top_label = (function_exists('jinr_breadcrumb_change_text') && jinr_breadcrumb_change_text() !== "") 
             ? jinr_breadcrumb_change_text() 
             : "TOP";
?>
<nav class="c-breadcrumb" aria-label="breadcrumb">
    <ul class="c-breadcrumb__list">
        
        <!-- Static Site Root Link -->
        <li class="c-breadcrumb__item">
            <a href="/">ユーピーエス</a>
        </li>

        <?php if (is_front_page() || is_home()) : ?>
            
            <!-- Home Page State: TOP is the current active item -->
            <li class="c-breadcrumb__item" aria-current="page">
                <?php echo esc_html($top_label); ?>
            </li>

        <?php else : ?>

            <!-- Internal Pages State: TOP is a link -->
            <li class="c-breadcrumb__item">
                <a href="<?php echo home_url('/'); ?>">
                    <?php echo esc_html($top_label); ?>
                </a>
            </li>

            <?php
            // Logic for Single Posts
            if (is_single()) {
                if (get_the_category() != false) {
                    $category = get_the_category();
                    $cat_parents = get_category_parents($category[0]->term_id, true, ':::');
                    $cat_array = explode(':::', $cat_parents);
                    foreach ($cat_array as $cat_link) {
                        if (!empty($cat_link)) {
                            echo '<li class="c-breadcrumb__item">' . $cat_link . '</li>';
                        }
                    }
                }
            }
            // Logic for Pages
            elseif (is_page()) {
                global $post;
                if (isset($post->post_parent) && $post->post_parent) {
                    $ancestors = array_reverse(get_post_ancestors($post->ID));
                    foreach ($ancestors as $ancestor) {
                        echo '<li class="c-breadcrumb__item"><a href="' . get_permalink($ancestor) . '">' . get_the_title($ancestor) . '</a></li>';
                    }
                }
            }
            // Logic for Category Archives
            elseif (is_category()) {
                global $cat;
                $ancestors = array_reverse(get_ancestors($cat, 'category'));
                foreach ($ancestors as $cat_id) {
                    echo '<li class="c-breadcrumb__item"><a href="' . get_category_link($cat_id) . '">' . get_category($cat_id)->name . '</a></li>';
                }
            }
            ?>

            <!-- Current Active Item for Internal Pages -->
            <li class="c-breadcrumb__item" aria-current="page">
                <?php
                if (is_search()) {
                    echo 'Search Results for "' . get_search_query() . '"';
                } elseif (is_404()) {
                    echo 'Page Not Found';
                } elseif (is_category()) {
                    single_cat_title();
                } else {
                    the_title();
                }
                ?>
            </li>

        <?php endif; ?>

    </ul>
</nav>