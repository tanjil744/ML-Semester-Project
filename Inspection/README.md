# Inspection

This module reads object detections from the model, counts each item, and checks whether the package contents match the expected packing list.

## Files

| File | Description |
|------|-------------|
| `inspector.py` | Main logic — counts items and compares with the packing list |
| `packing_list.json` | Expected items in one package |
| `test_inspector.py` | Unit tests |
| `demo.py` | Example outputs using simulated detections |

## Packing list

The expected package contains:

```json
{
  "pencil": 2,
  "eraser": 1,
  "ruler": 1
}
```

## How to run

Run the demo:
```bash
python Inspection/demo.py
```

Run the tests:
```bash
python Inspection/test_inspector.py
```

## Output example

```
Correct package: all required items are present.
Incorrect package: 1 pencil missing.
Incorrect package: 1 extra ruler.
```
