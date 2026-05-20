<?php
/**
 * Widget class for IBM Docs LLM
 */

class IBM_Docs_LLM_Widget {
    
    /**
     * Initialize widget
     */
    public static function init() {
        add_action('wp_footer', array(__CLASS__, 'render_floating_widget'));
    }
    
    /**
     * Render floating widget
     */
    public static function render_floating_widget() {
        if (!get_option('ibm_docs_llm_enable_widget', false)) {
            return;
        }
        
        $title = get_option('ibm_docs_llm_widget_title', __('Ask IBM Docs', 'ibm-docs-llm'));
        $placeholder = get_option('ibm_docs_llm_placeholder', __('Ask a question about IBM...', 'ibm-docs-llm'));
        $theme = get_option('ibm_docs_llm_theme', 'light');
        $position = get_option('ibm_docs_llm_position', 'bottom-right');
        
        self::render_widget_html($title, $placeholder, $theme, $position, true);
    }
    
    /**
     * Render widget HTML
     */
    public static function render_widget_html($title, $placeholder, $theme = 'light', $position = 'bottom-right', $floating = false) {
        $widget_class = 'ibm-docs-chat-widget';
        $widget_class .= ' theme-' . esc_attr($theme);
        $widget_class .= ' position-' . esc_attr($position);
        if ($floating) {
            $widget_class .= ' floating';
        }
        ?>
        <div id="ibm-docs-chat-widget" class="<?php echo $widget_class; ?>">
            <div class="chat-toggle" id="ibm-docs-chat-toggle">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            </div>
            
            <div class="chat-container" id="ibm-docs-chat-container">
                <div class="chat-header">
                    <h3><?php echo esc_html($title); ?></h3>
                    <div class="chat-actions">
                        <button class="chat-minimize" id="ibm-docs-chat-minimize" title="<?php esc_attr_e('Minimize', 'ibm-docs-llm'); ?>">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                        <button class="chat-close" id="ibm-docs-chat-close" title="<?php esc_attr_e('Close', 'ibm-docs-llm'); ?>">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="chat-messages" id="ibm-docs-chat-messages">
                    <div class="chat-message chat-message-assistant">
                        <div class="message-content">
                            <?php _e('Hello! I can help you with questions about IBM documentation. What would you like to know?', 'ibm-docs-llm'); ?>
                        </div>
                    </div>
                </div>
                
                <div class="chat-loading" id="ibm-docs-chat-loading" style="display: none;">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <form id="ibm-docs-chat-form">
                        <input 
                            type="text" 
                            id="ibm-docs-chat-input" 
                            class="chat-input" 
                            placeholder="<?php echo esc_attr($placeholder); ?>"
                            autocomplete="off">
                        <button type="submit" class="chat-submit" id="ibm-docs-chat-submit">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        </div>
        <?php
    }
}

// Made with Bob
