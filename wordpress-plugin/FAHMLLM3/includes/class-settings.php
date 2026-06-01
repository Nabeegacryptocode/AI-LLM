<?php
/**
 * Settings page for Fahm Faris
 */

class Fahm_Faris_Settings {
    
    /**
     * Initialize settings
     */
    public static function init() {
        add_action('admin_menu', array(__CLASS__, 'add_settings_page'));
        add_action('admin_init', array(__CLASS__, 'register_settings'));
    }
    
    /**
     * Add settings page to admin menu
     */
    public static function add_settings_page() {
        add_options_page(
            __('IBM Docs LLM Settings', 'ibm-docs-llm'),
            __('IBM Docs LLM', 'ibm-docs-llm'),
            'manage_options',
            'ibm-docs-llm',
            array(__CLASS__, 'render_settings_page')
        );
    }
    
    /**
     * Register settings
     */
    public static function register_settings() {
        // API Settings
        register_setting('fahm_faris_settings', 'fahm_faris_api_url', array(
            'type' => 'string',
            'sanitize_callback' => 'esc_url_raw',
            'default' => ''
        ));
        
        register_setting('fahm_faris_settings', 'fahm_faris_api_key', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => ''
        ));
        
        // Widget Settings
        register_setting('fahm_faris_settings', 'fahm_faris_enable_widget', array(
            'type' => 'boolean',
            'default' => false
        ));
        
        register_setting('fahm_faris_settings', 'fahm_faris_widget_title', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => __('FAHM Faris', 'fahm-faris')
        ));
        
        register_setting('fahm_faris_settings', 'fahm_faris_placeholder', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => __('Ask a question about IBM...', 'fahm-faris')
        ));
        
        register_setting('fahm_faris_settings', 'fahm_faris_theme', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => 'light'
        ));
        
        register_setting('fahm_faris_settings', 'fahm_faris_position', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => 'bottom-right'
        ));
        
        // Add settings sections
        add_settings_section(
            'fahm_faris_api_section',
            __('API Configuration', 'fahm-faris'),
            array(__CLASS__, 'render_api_section'),
            'fahm-faris'
        );
        
        add_settings_section(
            'fahm_faris_widget_section',
            __('Widget Settings', 'fahm-faris'),
            array(__CLASS__, 'render_widget_section'),
            'fahm-faris'
        );
        
        // Add settings fields
        add_settings_field(
            'fahm_faris_api_url',
            __('API URL', 'fahm-faris'),
            array(__CLASS__, 'render_api_url_field'),
            'fahm-faris',
            'fahm_faris_api_section'
        );
        
        add_settings_field(
            'fahm_faris_api_key',
            __('API Key', 'fahm-faris'),
            array(__CLASS__, 'render_api_key_field'),
            'fahm-faris',
            'fahm_faris_api_section'
        );
        
        add_settings_field(
            'fahm_faris_enable_widget',
            __('Enable Floating Widget', 'fahm-faris'),
            array(__CLASS__, 'render_enable_widget_field'),
            'fahm-faris',
            'fahm_faris_widget_section'
        );
        
        add_settings_field(
            'fahm_faris_widget_title',
            __('Widget Title', 'fahm-faris'),
            array(__CLASS__, 'render_widget_title_field'),
            'fahm-faris',
            'fahm_faris_widget_section'
        );
        
        add_settings_field(
            'fahm_faris_placeholder',
            __('Input Placeholder', 'fahm-faris'),
            array(__CLASS__, 'render_placeholder_field'),
            'fahm-faris',
            'fahm_faris_widget_section'
        );
        
        add_settings_field(
            'fahm_faris_theme',
            __('Theme', 'fahm-faris'),
            array(__CLASS__, 'render_theme_field'),
            'fahm-faris',
            'fahm_faris_widget_section'
        );
        
        add_settings_field(
            'fahm_faris_position',
            __('Widget Position', 'fahm-faris'),
            array(__CLASS__, 'render_position_field'),
            'fahm-faris',
            'fahm_faris_widget_section'
        );
    }
    
    /**
     * Render settings page
     */
    public static function render_settings_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        // Handle test connection
        if (isset($_POST['test_connection'])) {
            check_admin_referer('fahm_faris_test_connection');
            $api_client = new Fahm_Faris_API_Client();
            $result = $api_client->test_connection();
            
            if ($result['success']) {
                add_settings_error(
                    'fahm_faris_messages',
                    'fahm_faris_message',
                    $result['message'],
                    'success'
                );
            } else {
                add_settings_error(
                    'fahm_faris_messages',
                    'fahm_faris_message',
                    $result['message'],
                    'error'
                );
            }
        }
        
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            
            <?php settings_errors('fahm_faris_messages'); ?>
            
            <form action="options.php" method="post">
                <?php
                settings_fields('fahm_faris_settings');
                do_settings_sections('fahm-faris');
                submit_button(__('Save Settings', 'fahm-faris'));
                ?>
            </form>
            
            <form method="post" style="margin-top: 20px;">
                <?php wp_nonce_field('fahm_faris_test_connection'); ?>
                <?php submit_button(__('Test API Connection', 'fahm-faris'), 'secondary', 'test_connection', false); ?>
            </form>
            
            <div class="card" style="margin-top: 20px;">
                <h2><?php _e('Usage Instructions', 'fahm-faris'); ?></h2>
                <h3><?php _e('Shortcode', 'fahm-faris'); ?></h3>
                <p><?php _e('Add the chat widget to any page or post using:', 'fahm-faris'); ?></p>
                <code>[fahm_faris_chat]</code>
                
                <h3 style="margin-top: 20px;"><?php _e('Shortcode Parameters', 'fahm-faris'); ?></h3>
                <ul>
                    <li><code>title</code> - <?php _e('Widget title', 'fahm-faris'); ?></li>
                    <li><code>placeholder</code> - <?php _e('Input placeholder text', 'fahm-faris'); ?></li>
                    <li><code>theme</code> - <?php _e('Theme (light or dark)', 'fahm-faris'); ?></li>
                </ul>
                
                <p><?php _e('Example:', 'fahm-faris'); ?></p>
                <code>[fahm_faris_chat title="Ask Questions" theme="dark"]</code>
            </div>
        </div>
        <?php
    }
    
    /**
     * Render API section description
     */
    public static function render_api_section() {
        echo '<p>' . __('Configure the connection to your Fahm Faris backend API.', 'fahm-faris') . '</p>';
    }
    
    /**
     * Render widget section description
     */
    public static function render_widget_section() {
        echo '<p>' . __('Customize the appearance and behavior of the chat widget.', 'fahm-faris') . '</p>';
    }
    
    /**
     * Render API URL field
     */
    public static function render_api_url_field() {
        $value = get_option('fahm_faris_api_url', '');
        ?>
        <input type="url" 
               name="fahm_faris_api_url" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text"
               placeholder="https://your-api.railway.app">
        <p class="description">
            <?php _e('The URL of your backend API (e.g., https://your-api.railway.app)', 'fahm-faris'); ?>
        </p>
        <?php
    }
    
    /**
     * Render API key field
     */
    public static function render_api_key_field() {
        $value = get_option('fahm_faris_api_key', '');
        ?>
        <input type="password" 
               name="fahm_faris_api_key" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <p class="description">
            <?php _e('Your API key for authentication', 'fahm-faris'); ?>
        </p>
        <?php
    }
    
    /**
     * Render enable widget field
     */
    public static function render_enable_widget_field() {
        $value = get_option('fahm_faris_enable_widget', false);
        ?>
        <label>
            <input type="checkbox" 
                   name="fahm_faris_enable_widget" 
                   value="1" 
                   <?php checked($value, true); ?>>
            <?php _e('Show floating chat widget on all pages', 'fahm-faris'); ?>
        </label>
        <?php
    }
    
    /**
     * Render widget title field
     */
    public static function render_widget_title_field() {
        $value = get_option('fahm_faris_widget_title', __('FAHM Faris', 'fahm-faris'));
        ?>
        <input type="text" 
               name="fahm_faris_widget_title" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <?php
    }
    
    /**
     * Render placeholder field
     */
    public static function render_placeholder_field() {
        $value = get_option('fahm_faris_placeholder', __('Ask a question about IBM...', 'fahm-faris'));
        ?>
        <input type="text" 
               name="fahm_faris_placeholder" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <?php
    }
    
    /**
     * Render theme field
     */
    public static function render_theme_field() {
        $value = get_option('fahm_faris_theme', 'light');
        ?>
        <select name="fahm_faris_theme">
            <option value="light" <?php selected($value, 'light'); ?>><?php _e('Light', 'fahm-faris'); ?></option>
            <option value="dark" <?php selected($value, 'dark'); ?>><?php _e('Dark', 'fahm-faris'); ?></option>
        </select>
        <?php
    }
    
    /**
     * Render position field
     */
    public static function render_position_field() {
        $value = get_option('fahm_faris_position', 'bottom-right');
        ?>
        <select name="fahm_faris_position">
            <option value="bottom-right" <?php selected($value, 'bottom-right'); ?>><?php _e('Bottom Right', 'fahm-faris'); ?></option>
            <option value="bottom-left" <?php selected($value, 'bottom-left'); ?>><?php _e('Bottom Left', 'fahm-faris'); ?></option>
            <option value="top-right" <?php selected($value, 'top-right'); ?>><?php _e('Top Right', 'fahm-faris'); ?></option>
            <option value="top-left" <?php selected($value, 'top-left'); ?>><?php _e('Top Left', 'fahm-faris'); ?></option>
        </select>
        <?php
    }
}

// Made with Bob
