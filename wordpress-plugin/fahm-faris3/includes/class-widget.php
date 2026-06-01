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
                    Got a question? Ask FAHM Faris!
                </div>
            </div>
            <div class="chat-toggle" id="fahm-faris-chat-toggle">
                <div class="robot-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C11.45 2 11 2.45 11 3V4H8C6.9 4 6 4.9 6 6V8H4C3.45 8 3 8.45 3 9V11C3 11.55 3.45 12 4 12H6V20C6 21.1 6.9 22 8 22H16C17.1 22 18 21.1 18 20V12H20C20.55 12 21 11.55 21 11V9C21 8.45 20.55 8 20 8H18V6C18 4.9 17.1 4 16 4H13V3C13 2.45 12.55 2 12 2M9 9C9.55 9 10 9.45 10 10C10 10.55 9.55 11 9 11C8.45 11 8 10.55 8 10C8 9.45 8.45 9 9 9M15 9C15.55 9 16 9.45 16 10C16 10.55 15.55 11 15 11C14.45 11 14 10.55 14 10C14 9.45 14.45 9 15 9M12 17.5C10.07 17.5 8.5 15.93 8.5 14H15.5C15.5 15.93 13.93 17.5 12 17.5Z"/>
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
