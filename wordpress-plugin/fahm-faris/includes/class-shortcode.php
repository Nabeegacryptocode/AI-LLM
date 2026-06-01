<?php
/**
 * Shortcode handler for Fahm Faris
 */

class Fahm_Faris_Shortcode {
    
    /**
     * Initialize shortcode
     */
    public static function init() {
        add_shortcode('fahm_faris_chat', array(__CLASS__, 'render_shortcode'));
    }
    
    /**
     * Render shortcode
     */
    public static function render_shortcode($atts) {
        $atts = shortcode_atts(array(
            'title' => get_option('fahm_faris_widget_title', __('FAHM Faris', 'fahm-faris')),
            'placeholder' => get_option('fahm_faris_placeholder', __('Type your question here...', 'fahm-faris')),
            'theme' => get_option('fahm_faris_theme', 'light'),
            'height' => '600px'
        ), $atts, 'fahm_faris_chat');
        
        ob_start();
        ?>
        <div class="fahm-faris-chat-shortcode" style="height: <?php echo esc_attr($atts['height']); ?>;">
            <?php Fahm_Faris_Widget::render_widget_html(
                $atts['title'],
                $atts['placeholder'],
                $atts['theme'],
                'static',
                false
            ); ?>
        </div>
        <?php
        return ob_get_clean();
    }
}

// Made with Bob
