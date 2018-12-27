export default class Enum {
  constructor(definition) {
    this._enums = []
    this._lookups = {}

    for (const k in definition) {
      const j = definition[k]
      this[k] = j
      this.addEnum(j)
    }
    return this
  }

  getEnums() {
    return this._enums
  }

  addEnum(e) {
    this._enums.push(e)
  }

  forEach(callback) {
    const length = this._enums.length
    for (let i = 0; i < length; ++i) {
      callback(this._enums[i])
    }
  }

  getByName(name) {
    return this[name]
  }

  getByValue(field, value) {
    let lookup = this._lookups[field]
    if (lookup) {
      return lookup[value]
    } else {
      this._lookups[field] = (lookup = {})
      let k = this._enums.length - 1
      for (; k >= 0; --k) {
        const m = this._enums[k]
        const j = m[field]
        lookup[j] = m
        if (j == value) {
          return m
        }
      }
    }
    return null
  }
}

