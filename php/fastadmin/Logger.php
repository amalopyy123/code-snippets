<?php
/**
 * log内容到文件
 * \addons\common\library\Logger::log('message','test.log');
 * \addons\common\library\Logger::log([1,2,3],'test.log');
 * \addons\common\library\Logger::log(debug_backtrace(2),'test.log');
 *
 */
namespace addons\common\library; // Please replace 'common' with your actual addon directory name

/**
 * Optimized Independent Logger Class
 * Provides Laminas/Monolog (PSR-3) style logging capabilities with pretty array formatting.
 */
class Logger
{
    // Static cache for initialized directories to avoid redundant disk I/O (is_dir) per request
    private static $initializedDirs = [];

    /**
     * Core method for writing logs
     *
     * @param mixed  $content  Log content (supports string, array, object, Exception/Throwable)
     * @param string $filename Log filename (default is 'logger', without .log extension)
     * @param string $level    Log level (default is 'info')
     * @param array  $context  Contextual extra data (array format)
     * @return bool
     */
    public static function log($content, $filename = 'logger', $level = 'info', $context = [])
    {
        $logDir = RUNTIME_PATH . 'log' . DS . 'addons' . DS;

        // [Optimization 1: Reduce Disk I/O]
        // Check and create the directory only once per PHP request lifecycle
        if (!isset(self::$initializedDirs[$logDir])) {
            if (!is_dir($logDir)) {
                @mkdir($logDir, 0755, true);
            }
            self::$initializedDirs[$logDir] = true;
        }

        // Get the timestamp uniformly to prevent minor time differences
        $now = time();
        $date = date('Y-m-d', $now);
        $time = date('Y-m-d H:i:s', $now);
        $filePath = $logDir . $filename . '-' . $date . '.log';
        $level = strtoupper($level);

        // [Optimization 2: Robust Type Handling]
        // Specifically handle Exceptions/Throwables
        if ($content instanceof \Exception || $content instanceof \Throwable) {
            $content = (string) $content;
        } elseif (is_array($content) || is_object($content)) {
            // [Optimization 3: Pretty Print]
            // Added JSON_PRETTY_PRINT here! It formats the array with newlines and indents.
            $content = json_encode(
                $content,
                JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PARTIAL_OUTPUT_ON_ERROR | JSON_PRETTY_PRINT
            );
        }

        // [Optimization 4: PSR-3 Placeholder Interpolation]
        // Example: log("User {name} paid", "order", "info", ["name" => "John"])
        if (is_string($content) && !empty($context)) {
            $replace = [];
            foreach ($context as $key => $val) {
                if (is_scalar($val) || (is_object($val) && method_exists($val, '__toString'))) {
                    $replace['{' . $key . '}'] = $val;
                }
            }
            if (!empty($replace)) {
                $content = strtr($content, $replace);
            }
        }

        // Append context data with a newline for better readability when using pretty print
        if (!empty($context)) {
            $contextStr = json_encode(
                $context,
                JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PARTIAL_OUTPUT_ON_ERROR | JSON_PRETTY_PRINT
            );
            $content .= PHP_EOL . 'Context: ' . $contextStr;
        }

        // Format the final log line: [Time] [LEVEL] Content
        $logMessage = sprintf("[%s] [%s] %s" . PHP_EOL, $time, $level, $content);

        // [Optimization 5: Catch \Throwable]
        try {
            return file_put_contents($filePath, $logMessage, FILE_APPEND | LOCK_EX) !== false;
        } catch (\Throwable $e) {
            return false;
        }
    }

    /**
     * Shortcut method: Log INFO level
     */
    public static function info($content, $filename = 'logger', $context = [])
    {
        return self::log($content, $filename, 'INFO', $context);
    }

    /**
     * Shortcut method: Log ERROR level
     */
    public static function error($content, $filename = 'logger', $context = [])
    {
        return self::log($content, $filename, 'ERROR', $context);
    }

    /**
     * Shortcut method: Log DEBUG level
     */
    public static function debug($content, $filename = 'logger', $context = [])
    {
        return self::log($content, $filename, 'DEBUG', $context);
    }
}