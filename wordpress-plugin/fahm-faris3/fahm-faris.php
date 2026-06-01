<?php
/**
 * Plugin Name: Fahm Faris
 * Plugin URI: https://github.com/yourusername/fahm-faris
 * Description: AI-powered Q&A system using IBM documentation with RAG technology
 * Version: 1.0.0
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * Author: Fahm Technology Partners
 * Author URI: https://fahmtechnologypartners.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: fahm-faris
 * Domain Path: /languages
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('FAHM_FARIS_VERSION', '1.0.0');
define('FAHM_FARIS_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('FAHM_FARIS_PLUGIN_URL', plugin_dir_url(__FILE__));
define('FAHM_FARIS_PLUGIN_FILE', __FILE__);

// Include required files
require_once FAHM_FARIS_PLUGIN_DIR . 'includes/class-api-client.php';
require_once FAHM_FARIS_PLUGIN_DIR . 'includes/class-settings.php';
require_once FAHM_FARIS_PLUGIN_DIR . 'includes/class-widget.php';
require_once FAHM_FARIS_PLUGIN_DIR . 'includes/class-shortcode.php';

/**
 * Initialize the plugin
 */
function fahm_faris_init() {
    // Initialize settings
    Fahm_Faris_Settings::init();
    
    // Initialize widget
    Fahm_Faris_Widget::init();
    
    // Initialize shortcode
    Fahm_Faris_Shortcode::init();
    
    // Load text domain
    load_plugin_textdomain('fahm-faris', false, dirname(plugin_basename(__FILE__)) . '/languages');
}
add_action('plugins_loaded', 'fahm_faris_init');

/**
 * Enqueue frontend scripts and styles
 */
function fahm_faris_enqueue_scripts() {
    // Only load if widget is enabled or shortcode is present
    if (!fahm_faris_should_load_assets()) {
        return;
    }
    
    // Enqueue styles
    wp_enqueue_style(
        'fahm-faris-chat',
        FAHM_FARIS_PLUGIN_URL . 'public/css/chat-widget.css',
        array(),
        FAHM_FARIS_VERSION
    );
    
    // Enqueue scripts
    wp_enqueue_script(
        'fahm-faris-chat',
        FAHM_FARIS_PLUGIN_URL . 'public/js/chat-widget.js',
        array('jquery'),
        FAHM_FARIS_VERSION,
        true
    );
    
    // Localize script with settings
    wp_localize_script('fahm-faris-chat', 'fahmFaris', array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('fahm_faris_nonce'),
        'apiUrl' => get_option('fahm_faris_api_url', ''),
        'apiKey' => get_option('fahm_faris_api_key', ''),
        'widgetTitle' => get_option('fahm_faris_widget_title', __('Ask Fahm Faris', 'fahm-faris')),
        'placeholder' => get_option('fahm_faris_placeholder', __('Ask a question about IBM...', 'fahm-faris')),
        'theme' => get_option('fahm_faris_theme', 'light'),
        'position' => get_option('fahm_faris_position', 'bottom-left'),
        'strings' => array(
            'send' => __('Send', 'fahm-faris'),
            'thinking' => __('Thinking...', 'fahm-faris'),
            'error' => __('Sorry, there was an error processing your request.', 'fahm-faris'),
            'close' => __('Close', 'fahm-faris'),
            'minimize' => __('Minimize', 'fahm-faris')
        )
    ));
}
add_action('wp_enqueue_scripts', 'fahm_faris_enqueue_scripts');

/**
 * Enqueue admin scripts and styles
 */
function fahm_faris_admin_enqueue_scripts($hook) {
    // Only load on plugin settings page
    if ($hook !== 'settings_page_fahm-faris') {
        return;
    }
    
    wp_enqueue_style(
        'fahm-faris-admin',
        FAHM_FARIS_PLUGIN_URL . 'admin/css/admin.css',
        array(),
        FAHM_FARIS_VERSION
    );
    
    wp_enqueue_script(
        'fahm-faris-admin',
        FAHM_FARIS_PLUGIN_URL . 'admin/js/admin.js',
        array('jquery'),
        FAHM_FARIS_VERSION,
        true
    );
}
add_action('admin_enqueue_scripts', 'fahm_faris_admin_enqueue_scripts');

/**
 * Check if assets should be loaded
 */
function fahm_faris_should_load_assets() {
    global $post;
    
    // Check if floating widget is enabled
    if (get_option('fahm_faris_enable_widget', false)) {
        return true;
    }
    
    // Check if shortcode is present in content
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'fahm_faris_chat')) {
        return true;
    }
    
    return false;
}

/**
 * Register REST API endpoints
 */
function fahm_faris_register_rest_routes() {
    register_rest_route('fahm-faris/v1', '/chat', array(
        'methods' => 'POST',
        'callback' => 'fahm_faris_handle_chat',
        'permission_callback' => '__return_true'
    ));
    
    register_rest_route('fahm-faris/v1', '/test-connection', array(
        'methods' => 'POST',
        'callback' => 'fahm_faris_test_connection',
        'permission_callback' => 'fahm_faris_check_admin_permission'
    ));
}
add_action('rest_api_init', 'fahm_faris_register_rest_routes');

/**
 * Handle chat request
 */
function fahm_faris_handle_chat($request) {
    // Verify nonce
    $nonce = $request->get_header('X-WP-Nonce');
    if (!wp_verify_nonce($nonce, 'wp_rest')) {
        return new WP_Error('invalid_nonce', __('Invalid nonce', 'fahm-faris'), array('status' => 403));
    }
    
    $question = sanitize_text_field($request->get_param('question'));
    $conversation_id = sanitize_text_field($request->get_param('conversation_id'));
    
    if (empty($question)) {
        return new WP_Error('empty_question', __('Question cannot be empty', 'fahm-faris'), array('status' => 400));
    }
    
    // Call backend API
    $api_client = new Fahm_Faris_API_Client();
    $response = $api_client->send_chat_request($question, $conversation_id);
    
    if (is_wp_error($response)) {
        return $response;
    }
    
    return rest_ensure_response($response);
}

/**
 * Test API connection
 */
function fahm_faris_test_connection($request) {
    $api_url = sanitize_text_field($request->get_param('api_url'));
    $api_key = sanitize_text_field($request->get_param('api_key'));
    
    $api_client = new Fahm_Faris_API_Client($api_url, $api_key);
    $result = $api_client->test_connection();
    
    return rest_ensure_response($result);
}

/**
 * Check admin permission
 */
function fahm_faris_check_admin_permission() {
    return current_user_can('manage_options');
}

/**
 * AJAX handler for chat (fallback)
 */
function fahm_faris_ajax_chat() {
    check_ajax_referer('fahm_faris_nonce', 'nonce');
    
    $question = sanitize_text_field($_POST['question']);
    $conversation_id = sanitize_text_field($_POST['conversation_id'] ?? '');
    
    if (empty($question)) {
        wp_send_json_error(array('message' => __('Question cannot be empty', 'fahm-faris')));
    }
    
    $api_client = new Fahm_Faris_API_Client();
    $response = $api_client->send_chat_request($question, $conversation_id);
    
    if (is_wp_error($response)) {
        wp_send_json_error(array('message' => $response->get_error_message()));
    }
    
    wp_send_json_success($response);
}
add_action('wp_ajax_fahm_faris_chat', 'fahm_faris_ajax_chat');
add_action('wp_ajax_nopriv_fahm_faris_chat', 'fahm_faris_ajax_chat');

/**
 * Activation hook
 */
function fahm_faris_activate() {
    // Set default options
    add_option('fahm_faris_widget_title', __('FAHM Faris', 'fahm-faris'));
    add_option('fahm_faris_placeholder', __('Type your question here...', 'fahm-faris'));
    add_option('fahm_faris_theme', 'light');
    add_option('fahm_faris_position', 'bottom-right');
    add_option('fahm_faris_enable_widget', false);
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'fahm_faris_activate');

/**
 * Deactivation hook
 */
function fahm_faris_deactivate() {
    // Flush rewrite rules
    flush_rewrite_rules();
}
register_deactivation_hook(__FILE__, 'fahm_faris_deactivate');

// Made with Bob
