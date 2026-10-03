package rilavo

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// Canonicalize produces JCS-subset canonical JSON bytes matching
// rilavo.canonical.canonicalize exactly for string + integer values.
// Floats are rejected; booleans are not expected in credential fields.
func Canonicalize(fields map[string]interface{}) ([]byte, error) {
	var sb strings.Builder
	if err := canonValue(&sb, fields, 0); err != nil {
		return nil, err
	}
	return []byte(sb.String()), nil
}

func canonValue(sb *strings.Builder, v interface{}, depth int) error {
	switch val := v.(type) {
	case string:
		sb.WriteString(canonString(val))
	case float64:
		// JSON numbers arrive as float64; reject non-integral values.
		i := int64(val)
		if float64(i) != val {
			return fmt.Errorf("floats are not representable in Rilavo credentials")
		}
		sb.WriteString(fmt.Sprintf("%d", i))
	case int:
		sb.WriteString(fmt.Sprintf("%d", val))
	case int64:
		sb.WriteString(fmt.Sprintf("%d", val))
	case json.Number:
		i, err := val.Int64()
		if err != nil {
			return fmt.Errorf("floats are not representable in Rilavo credentials")
		}
		sb.WriteString(fmt.Sprintf("%d", i))
	case bool:
		return fmt.Errorf("booleans not expected in Rilavo credential fields")
	case nil:
		return fmt.Errorf("null not expected in Rilavo credential fields")
	case []interface{}:
		sb.WriteString("[")
		for j, item := range val {
			if j > 0 {
				sb.WriteString(",")
			}
			if err := canonValue(sb, item, depth+1); err != nil {
				return err
			}
		}
		sb.WriteString("]")
	case map[string]interface{}:
		keys := make([]string, 0, len(val))
		for k := range val {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		sb.WriteString("{")
		for j, k := range keys {
			if j > 0 {
				sb.WriteString(",")
			}
			sb.WriteString(canonString(k))
			sb.WriteString(":")
			if err := canonValue(sb, val[k], depth+1); err != nil {
				return err
			}
		}
		sb.WriteString("}")
	default:
		return fmt.Errorf("unsupported type: %T", v)
	}
	return nil
}

func canonString(s string) string {
	var sb strings.Builder
	sb.WriteByte('"')
	for _, r := range s {
		switch {
		case r == '"':
			sb.WriteString(`\"`)
		case r == '\\':
			sb.WriteString(`\\`)
		case r == '\b':
			sb.WriteString(`\b`)
		case r == '\f':
			sb.WriteString(`\f`)
		case r == '\n':
			sb.WriteString(`\n`)
		case r == '\r':
			sb.WriteString(`\r`)
		case r == '\t':
			sb.WriteString(`\t`)
		case r < 0x20:
			sb.WriteString(fmt.Sprintf(`\u%04x`, r))
		default:
			sb.WriteRune(r)
		}
	}
	sb.WriteByte('"')
	return sb.String()
}

// ParseCredentialFields parses a raw JSON credential into a generic map,
// using json.Number to preserve integer precision.
func ParseCredentialFields(data []byte) (map[string]interface{}, error) {
	var result map[string]interface{}
	dec := json.NewDecoder(strings.NewReader(string(data)))
	dec.UseNumber()
	if err := dec.Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}
