<?php
/**
 * 用于在各种页面显示副标题
 * 引入：
 * <?php get_template_part('tosho-p-page-header'); ?>
 */
/**
 * Component: Universal Page Header
 * File: tosho-p-page-header.php
 */
$show_breadcrumb = ! is_home() && ! is_front_page();
?>
<section class="p-page-header">
    <div class="p-page-header__inner">

        <?php if ($show_breadcrumb) : ?>
            <!-- Breadcrumb Navigation Wrapper -->
            <div class="p-page-header__breadcrumb-wrapper">
                <?php 
                /**
                 * Load the breadcrumb component
                 * File: tosho-c-breadcrumb.php
                 */
                get_template_part('tosho-c-breadcrumb'); 
                ?>
            </div>
        <?php endif; ?>

        <!-- Title Area -->
        <div class="p-page-header__title-area">
            <span class="p-page-header__subtitle">
                <?php
                if (is_single() && get_the_category()) {
                    // Show first category name for posts
                    $cats = get_the_category();
                    echo esc_html($cats[0]->name);
                } elseif (is_page()) {
                    // Show page slug as subtitle
                    global $post;
                    echo strtoupper($post->post_name);
                } elseif (is_category()) {
                    echo 'CATEGORY'; 
                }
                ?>
            </span>
            <h1 class="p-page-header__main-title">
                <?php 
                if (is_category()) { 
                    single_cat_title();
                } else {
                    the_title();
                }
                ?>
            </h1>
            <div class="p-page-header__line"></div>
        </div>

    </div>
</section>