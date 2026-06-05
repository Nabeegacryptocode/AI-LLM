<?php
/**
 * Plugin Name: Fahm Faris
 * Plugin URI: https://github.com/yourusername/fahm-faris
 * Description: FAHM Personal AI Assistant
 * Version: 1.0.4
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * Author: Fahm Technology Partners
 * Author URI: https://fahmpartners.com
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
 * Enqueue scripts and styles
 */
function fahm_faris_enqueue_scripts() {
    // Enqueue CSS
    wp_enqueue_style(
        'fahm-faris-chat-widget',
        FAHM_FARIS_PLUGIN_URL . 'public/css/chat-widget.css',
        array(),
        FAHM_FARIS_VERSION
    );
    
    // Enqueue jQuery
    wp_enqueue_script('jquery');
    
    // Enqueue JS
    wp_enqueue_script(
        'fahm-faris-chat-widget',
        FAHM_FARIS_PLUGIN_URL . 'public/js/chat-widget.js',
        array('jquery'),
        FAHM_FARIS_VERSION,
        true
    );
    
    // Localize script
    wp_localize_script('fahm-faris-chat-widget', 'fahmFaris', array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('fahm_faris_chat'),
        'strings' => array(
            'error' => __('Sorry, something went wrong. Please try again.', 'fahm-faris'),
            'sending' => __('Sending...', 'fahm-faris')
        )
    ));
}
add_action('wp_enqueue_scripts', 'fahm_faris_enqueue_scripts');

/**
 * Handle AJAX chat request
 */
function fahm_faris_handle_chat() {
    check_ajax_referer('fahm_faris_chat', 'nonce');
    
    $question = isset($_POST['question']) ? sanitize_text_field($_POST['question']) : '';
    $conversation_id = isset($_POST['conversation_id']) ? sanitize_text_field($_POST['conversation_id']) : null;
    
    if (empty($question)) {
        wp_send_json_error(array('message' => __('Question is required', 'fahm-faris')));
    }
    
    $api_client = new Fahm_Faris_API_Client();
    $result = $api_client->send_chat_request($question, $conversation_id);
    
    if (is_wp_error($result)) {
        wp_send_json_error(array('message' => $result->get_error_message()));
    }
    
    wp_send_json_success($result);
}
add_action('wp_ajax_fahm_faris_chat', 'fahm_faris_handle_chat');
add_action('wp_ajax_nopriv_fahm_faris_chat', 'fahm_faris_handle_chat');


