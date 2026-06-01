<?php
/**
 * Widget class for Fahm Faris
 */

class Fahm_Faris_Widget {
    
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
        if (!get_option('fahm_faris_enable_widget', false)) {
            return;
        }
        
        $title = get_option('fahm_faris_widget_title', __('FAHM Faris', 'fahm-faris'));
        $placeholder = get_option('fahm_faris_placeholder', __('Type your question here...', 'fahm-faris'));
        $theme = get_option('fahm_faris_theme', 'light');
        $position = get_option('fahm_faris_position', 'bottom-right');
        
        self::render_widget_html($title, $placeholder, $theme, $position, true);
    }
    
    /**
     * Render widget HTML
     */
    public static function render_widget_html($title, $placeholder, $theme = 'light', $position = 'bottom-right', $floating = false) {
        $widget_class = 'fahm-faris-chat-widget';
        $widget_class .= ' theme-' . esc_attr($theme);
        $widget_class .= ' position-' . esc_attr($position);
        if ($floating) {
            $widget_class .= ' floating';
        }
        ?>
        <div id="fahm-faris-chat-widget" class="<?php echo $widget_class; ?>">
            <div class="chat-prompt" id="fahm-faris-chat-prompt">
                <div class="prompt-bubble">
                    <span class="prompt-text">Got a question? Ask FAHM Faris!</span>
                    <button class="prompt-close" id="fahm-faris-prompt-close" aria-label="Close prompt">×</button>
                </div>
            </div>
            <div class="chat-toggle" id="fahm-faris-chat-toggle">
                <div class="robot-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="11" width="18" height="10" rx="2" ry="2"></rect>
                        <circle cx="12" cy="5" r="2"></circle>
                        <path d="M12 7v4"></path>
                        <line x1="8" y1="16" x2="8" y2="16"></line>
                        <line x1="16" y1="16" x2="16" y2="16"></line>
                    </svg>
                </div>
            </div>
            
            <div class="chat-container" id="fahm-faris-chat-container">
                <div class="chat-header">
                    <h3><?php echo esc_html($title); ?></h3>
                    <div class="chat-actions">
                        <button class="chat-minimize" id="fahm-faris-chat-minimize" title="<?php esc_attr_e('Minimize', 'fahm-faris'); ?>">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                        <button class="chat-close" id="fahm-faris-chat-close" title="<?php esc_attr_e('Close', 'fahm-faris'); ?>">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="chat-messages" id="fahm-faris-chat-messages">
                    <div class="chat-message chat-message-assistant">
                        <div class="message-content">
                            <?php _e('Hello! I can help you with questions about IBM documentation. What would you like to know?', 'fahm-faris'); ?>
                        </div>
                    </div>
                </div>
                
                <div class="chat-loading" id="fahm-faris-chat-loading" style="display: none;">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <form id="fahm-faris-chat-form">
                        <input 
                            type="text" 
                            id="fahm-faris-chat-input" 
                            class="chat-input" 
                            placeholder="<?php echo esc_attr($placeholder); ?>"
                            autocomplete="off">
                        <button type="submit" class="chat-submit" id="fahm-faris-chat-submit">
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
