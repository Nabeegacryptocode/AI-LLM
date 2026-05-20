<?php
/**
 * Shortcode handler for IBM Docs LLM
 */

class IBM_Docs_LLM_Shortcode {
    
    /**
     * Initialize shortcode
     */
    public static function init() {
        add_shortcode('ibm_docs_chat', array(__CLASS__, 'render_shortcode'));
    }
    
    /**
     * Render shortcode
     */
    public static function render_shortcode($atts) {
        $atts = shortcode_atts(array(
            'title' => get_option('ibm_docs_llm_widget_title', __('Ask IBM Docs', 'ibm-docs-llm')),
            'placeholder' => get_option('ibm_docs_llm_placeholder', __('Ask a question about IBM...', 'ibm-docs-llm')),
            'theme' => get_option('ibm_docs_llm_theme', 'light'),
            'height' => '600px'
        ), $atts, 'ibm_docs_chat');
        
        ob_start();
        ?>
        <div class="ibm-docs-chat-shortcode" style="height: <?php echo esc_attr($atts['height']); ?>;">
            <?php IBM_Docs_LLM_Widget::render_widget_html(
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
