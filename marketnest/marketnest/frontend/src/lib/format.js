const nf = new Intl.NumberFormat('en-PK', { maximumFractionDigits: 0 })
export const pkr = (n) => `Rs ${nf.format(Math.round(Number(n) || 0))}`
export const discount = (price, compare) =>
  compare && Number(compare) > Number(price) ? Math.round((1 - Number(price) / Number(compare)) * 100) : 0
export const shortDate = (iso) =>
  new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

export const FREE_SHIPPING_FROM = 5000
export const SHIPPING_FEE = 250

export const ORDER_STEPS = ['pending', 'packed', 'shipped', 'delivered']
export const STEP_LABEL = { pending: 'Waiting for the stall', packed: 'Packed', shipped: 'On the way', delivered: 'Delivered', cancelled: 'Cancelled' }
