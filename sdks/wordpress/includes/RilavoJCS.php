<?php

namespace Rilavo;
/**
 * JCS subset canonical JSON serializer.
 * Byte-compatible with Python canonical.py and TS jcs.ts for string+integer values.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

final class RilavoJCS {

    /**
     * Canonicalize an associative array (string keys, string|int values only).
     * Returns canonical JSON bytes or throws InvalidArgumentException on floats/bools/null.
     *
     * @param array<string,mixed> $fields Credential fields to serialize.
     * @return string Canonical JSON string.
     * @throws InvalidArgumentException On unsupported value types.
     */
    public static function canonicalize(array $fields): string {
        return self::serializeValue($fields);
    }

    private static function serializeValue($value): string {
        if (is_string($value)) {
            return self::escapeString($value);
        }
        if (is_int($value)) {
            return (string) $value;
        }
        if (is_float($value)) {
            throw new InvalidArgumentException('floats are not representable in Rilavo credentials');
        }
        if (is_bool($value)) {
            throw new InvalidArgumentException('booleans not expected in Rilavo credential fields');
        }
        if (is_null($value)) {
            throw new InvalidArgumentException('null not expected in Rilavo credential fields');
        }
        if (is_array($value)) {
            // PHP arrays: check if associative (string keys = object).
            $is_object = count(array_filter(array_keys($value), 'is_string')) > 0;
            if ($is_object) {
                $keys = array_keys($value);
                sort($keys, SORT_STRING);
                $pairs = [];
                foreach ($keys as $k) {
                    $pairs[] = self::escapeString((string)$k) . ':' . self::serializeValue($value[$k]);
                }
                return '{' . implode(',', $pairs) . '}';
            }
            // Sequential array = JSON array.
            $items = [];
            foreach ($value as $item) {
                $items[] = self::serializeValue($item);
            }
            return '[' . implode(',', $items) . ']';
        }
        throw new InvalidArgumentException('unsupported type: ' . gettype($value));
    }

    private static function escapeString(string $s): string {
        $out = '"';
        $len = strlen($s);
        for ($i = 0; $i < $len; $i++) {
            $c = $s[$i];
            switch ($c) {
                case '"':  $out .= '\"'; break;
                case '\\': $out .= '\\\\'; break;
                case "\b": $out .= '\b'; break;
                case "\f": $out .= '\f'; break;
                case "\n": $out .= '\n'; break;
                case "\r": $out .= '\r'; break;
                case "\t": $out .= '\t'; break;
                default:
                    $ord = ord($c);
                    if ($ord < 0x20) {
                        $out .= sprintf('\u%04x', $ord);
                    } else {
                        $out .= $c;
                    }
            }
        }
        $out .= '"';
        return $out;
    }

    /**
     * Public wrapper for escapeString (used by verifier for PoP payload).
     */
    public static function escapeStringPublic(string $s): string {
        return self::escapeString($s);
    }
}
