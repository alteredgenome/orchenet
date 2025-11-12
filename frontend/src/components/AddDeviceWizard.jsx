import React, { useState } from 'react'
import { X, ChevronRight, ChevronLeft, Check, Copy, Download } from 'lucide-react'
import api from '../services/api'

const VENDORS = [
  { id: 'mikrotik', name: 'MikroTik', enabled: true, icon: '🔷' },
  { id: 'fortinet', name: 'FortiGate', enabled: false, icon: '🔴' },
  { id: 'watchguard', name: 'WatchGuard', enabled: false, icon: '🟠' },
  { id: 'ubiquiti', name: 'Ubiquiti', enabled: false, icon: '🔵' }
]

const MIKROTIK_MODELS = [
  { id: 'routerboard', name: 'RouterBoard', enabled: true },
  { id: 'ccr', name: 'Cloud Core Router (CCR)', enabled: false },
  { id: 'hex', name: 'hEX Series', enabled: false },
  { id: 'rb5009', name: 'RB5009', enabled: false },
  { id: 'other', name: 'Other MikroTik', enabled: false }
]

function AddDeviceWizard({ isOpen, onClose, onSuccess }) {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Form data
  const [formData, setFormData] = useState({
    vendor: 'mikrotik',
    model: 'routerboard',
    deviceName: '',
    macAddress: '',
    location: '',
    description: ''
  })

  // Generated data
  const [deviceId, setDeviceId] = useState(null)
  const [provisionScript, setProvisionScript] = useState('')
  const [scriptFilename, setScriptFilename] = useState('')
  const [wireguardInfo, setWireguardInfo] = useState(null)

  const totalSteps = 4

  const handleNext = async () => {
    setError(null)

    if (step === 1) {
      // Validate vendor selection
      if (!formData.vendor) {
        setError('Please select a vendor')
        return
      }
      setStep(2)
    } else if (step === 2) {
      // Validate device type and basic info
      if (!formData.model) {
        setError('Please select a device type')
        return
      }
      if (!formData.deviceName.trim()) {
        setError('Please enter a device name')
        return
      }
      if (!formData.macAddress.trim()) {
        setError('Please enter the device MAC address')
        return
      }

      // Validate MAC address format
      const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/
      if (!macRegex.test(formData.macAddress)) {
        setError('Invalid MAC address format. Use format: XX:XX:XX:XX:XX:XX')
        return
      }

      setStep(3)
    } else if (step === 3) {
      // Create device and generate provisioning script
      await handleCreateDevice()
    }
  }

  const handleBack = () => {
    setError(null)
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleCreateDevice = async () => {
    setLoading(true)
    setError(null)

    try {
      // Step 1: Create device in backend
      const deviceResponse = await api.post('/api/devices', {
        name: formData.deviceName,
        vendor: formData.vendor,
        model: formData.model,
        mac_address: formData.macAddress,
        check_in_method: 'http',
        check_in_interval: 300, // 5 minutes
        device_data: {
          location: formData.location,
          description: formData.description
        }
      })

      const newDeviceId = deviceResponse.data.id
      setDeviceId(newDeviceId)

      // Step 2: Generate provisioning script
      const scriptResponse = await api.post('/api/devices/provision-script', {
        device_id: newDeviceId,
        mac_address: formData.macAddress
      })

      setProvisionScript(scriptResponse.data.script)
      setScriptFilename(scriptResponse.data.filename)
      setWireguardInfo(scriptResponse.data.wireguard_info)

      setStep(4)
    } catch (err) {
      console.error('Error creating device:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create device. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyScript = () => {
    navigator.clipboard.writeText(provisionScript)
    alert('Provisioning script copied to clipboard!')
  }

  const handleDownloadScript = () => {
    const blob = new Blob([provisionScript], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = scriptFilename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleFinish = () => {
    onSuccess()
    onClose()
  }

  const formatMacForTunnel = (mac) => {
    return mac.replace(/:/g, '_').toLowerCase()
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={(e) => e.target.className === 'modal-overlay' && onClose()}>
      <div className="modal-content" style={{ maxWidth: '800px', maxHeight: '90vh', overflow: 'auto' }}>
        <div className="modal-header">
          <h2>Add New Device</h2>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Progress Indicator */}
        <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            {[1, 2, 3, 4].map(num => (
              <div key={num} style={{ flex: 1, textAlign: 'center' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: num <= step ? 'var(--accent-blue)' : 'var(--border-color)',
                  color: 'white',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  marginBottom: '5px'
                }}>
                  {num < step ? <Check size={16} /> : num}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {num === 1 && 'Vendor'}
                  {num === 2 && 'Device Info'}
                  {num === 3 && 'Review'}
                  {num === 4 && 'Script'}
                </div>
              </div>
            ))}
          </div>
          <div style={{
            height: '4px',
            background: 'var(--border-color)',
            borderRadius: '2px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${(step / totalSteps) * 100}%`,
              height: '100%',
              background: 'var(--accent-blue)',
              transition: 'width 0.3s'
            }} />
          </div>
        </div>

        <div className="modal-body">
          {error && (
            <div style={{
              padding: '12px',
              background: 'var(--accent-red)',
              color: 'white',
              borderRadius: '4px',
              marginBottom: '20px'
            }}>
              {error}
            </div>
          )}

          {/* Step 1: Select Vendor */}
          {step === 1 && (
            <div>
              <h3 style={{ marginBottom: '20px' }}>Select Device Vendor</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                {VENDORS.map(vendor => (
                  <div
                    key={vendor.id}
                    onClick={() => vendor.enabled && setFormData({ ...formData, vendor: vendor.id })}
                    style={{
                      padding: '20px',
                      border: `2px solid ${formData.vendor === vendor.id ? 'var(--accent-blue)' : 'var(--border-color)'}`,
                      borderRadius: '8px',
                      cursor: vendor.enabled ? 'pointer' : 'not-allowed',
                      textAlign: 'center',
                      opacity: vendor.enabled ? 1 : 0.5,
                      background: formData.vendor === vendor.id ? 'var(--card-bg)' : 'transparent',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>{vendor.icon}</div>
                    <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{vendor.name}</div>
                    {!vendor.enabled && (
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Coming Soon</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Device Type and Info */}
          {step === 2 && (
            <div>
              <h3 style={{ marginBottom: '20px' }}>Device Information</h3>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Device Type *
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                  {MIKROTIK_MODELS.map(model => (
                    <div
                      key={model.id}
                      onClick={() => model.enabled && setFormData({ ...formData, model: model.id })}
                      style={{
                        padding: '15px',
                        border: `2px solid ${formData.model === model.id ? 'var(--accent-blue)' : 'var(--border-color)'}`,
                        borderRadius: '8px',
                        cursor: model.enabled ? 'pointer' : 'not-allowed',
                        opacity: model.enabled ? 1 : 0.5,
                        background: formData.model === model.id ? 'var(--card-bg)' : 'transparent',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ fontWeight: 'bold' }}>{model.name}</div>
                      {!model.enabled && (
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '5px' }}>
                          Coming Soon
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Device Name *
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g., FW-HQ-01"
                  value={formData.deviceName}
                  onChange={(e) => setFormData({ ...formData, deviceName: e.target.value })}
                />
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '5px' }}>
                  A unique name to identify this device
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  MAC Address *
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="XX:XX:XX:XX:XX:XX"
                  value={formData.macAddress}
                  onChange={(e) => setFormData({ ...formData, macAddress: e.target.value.toUpperCase() })}
                  style={{ fontFamily: 'monospace' }}
                />
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '5px' }}>
                  Used for WireGuard tunnel naming: orcatun_{formatMacForTunnel(formData.macAddress || 'xx_xx_xx_xx_xx_xx')}
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Location (Optional)
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g., Headquarters, Branch Office 1"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Description (Optional)
                </label>
                <textarea
                  className="form-control"
                  placeholder="Additional notes about this device..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div>
              <h3 style={{ marginBottom: '20px' }}>Review Device Configuration</h3>

              <div style={{
                background: 'var(--card-bg)',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px'
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', gap: '15px' }}>
                  <div style={{ fontWeight: 'bold' }}>Vendor:</div>
                  <div>{VENDORS.find(v => v.id === formData.vendor)?.name}</div>

                  <div style={{ fontWeight: 'bold' }}>Device Type:</div>
                  <div>{MIKROTIK_MODELS.find(m => m.id === formData.model)?.name}</div>

                  <div style={{ fontWeight: 'bold' }}>Device Name:</div>
                  <div>{formData.deviceName}</div>

                  <div style={{ fontWeight: 'bold' }}>MAC Address:</div>
                  <div style={{ fontFamily: 'monospace' }}>{formData.macAddress}</div>

                  <div style={{ fontWeight: 'bold' }}>Tunnel Name:</div>
                  <div style={{ fontFamily: 'monospace', color: 'var(--accent-blue)' }}>
                    orcatun_{formatMacForTunnel(formData.macAddress)}
                  </div>

                  {formData.location && (
                    <>
                      <div style={{ fontWeight: 'bold' }}>Location:</div>
                      <div>{formData.location}</div>
                    </>
                  )}

                  {formData.description && (
                    <>
                      <div style={{ fontWeight: 'bold' }}>Description:</div>
                      <div>{formData.description}</div>
                    </>
                  )}
                </div>
              </div>

              <div style={{
                padding: '15px',
                background: 'var(--accent-blue)',
                color: 'white',
                borderRadius: '8px',
                fontSize: '14px'
              }}>
                <strong>Next Step:</strong> We'll create the device and generate a provisioning script that you can run on your MikroTik router to establish the WireGuard tunnel and enable automatic check-ins.
              </div>
            </div>
          )}

          {/* Step 4: Provisioning Script */}
          {step === 4 && (
            <div>
              <h3 style={{ marginBottom: '20px' }}>
                <Check size={24} style={{ color: 'var(--accent-green)', marginRight: '10px' }} />
                Device Created Successfully!
              </h3>

              {wireguardInfo && (
                <div style={{
                  background: 'var(--card-bg)',
                  padding: '20px',
                  borderRadius: '8px',
                  marginBottom: '20px'
                }}>
                  <h4 style={{ marginBottom: '15px' }}>WireGuard Configuration</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', gap: '10px', fontSize: '14px' }}>
                    <div style={{ fontWeight: 'bold' }}>Tunnel Name:</div>
                    <div style={{ fontFamily: 'monospace', color: 'var(--accent-blue)' }}>
                      orcatun_{formatMacForTunnel(formData.macAddress)}
                    </div>

                    <div style={{ fontWeight: 'bold' }}>VPN IP:</div>
                    <div style={{ fontFamily: 'monospace' }}>{wireguardInfo.vpn_ip}</div>

                    <div style={{ fontWeight: 'bold' }}>Server IP:</div>
                    <div style={{ fontFamily: 'monospace' }}>{wireguardInfo.server_ip}</div>
                  </div>
                </div>
              )}

              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <h4>Provisioning Script</h4>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn btn-secondary" onClick={handleCopyScript}>
                      <Copy size={16} />
                      Copy
                    </button>
                    <button className="btn btn-secondary" onClick={handleDownloadScript}>
                      <Download size={16} />
                      Download
                    </button>
                  </div>
                </div>

                <textarea
                  readOnly
                  value={provisionScript}
                  style={{
                    width: '100%',
                    height: '300px',
                    fontFamily: 'monospace',
                    fontSize: '12px',
                    background: 'var(--sidebar-bg)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '4px',
                    padding: '10px'
                  }}
                />
              </div>

              <div style={{
                padding: '15px',
                background: 'var(--accent-green)',
                color: 'white',
                borderRadius: '8px',
                fontSize: '14px',
                marginBottom: '10px'
              }}>
                <strong>Installation Steps:</strong>
                <ol style={{ marginTop: '10px', marginBottom: '0', paddingLeft: '20px' }}>
                  <li>Copy the script above to your MikroTik router (via Winbox, SCP, or paste in terminal)</li>
                  <li>Run: <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 6px', borderRadius: '3px' }}>/import {scriptFilename}</code></li>
                  <li>Change default SSH password: <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 6px', borderRadius: '3px' }}>/user set orchenet password=YOUR_PASSWORD</code></li>
                  <li>Device will appear in the dashboard within 5 minutes</li>
                </ol>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          {step < 4 && (
            <>
              <button className="btn btn-secondary" onClick={step === 1 ? onClose : handleBack} disabled={loading}>
                <ChevronLeft size={16} />
                {step === 1 ? 'Cancel' : 'Back'}
              </button>
              <button className="btn btn-primary" onClick={handleNext} disabled={loading}>
                {loading ? 'Creating...' : step === 3 ? 'Create Device' : 'Next'}
                {!loading && <ChevronRight size={16} />}
              </button>
            </>
          )}
          {step === 4 && (
            <button className="btn btn-primary" onClick={handleFinish} style={{ marginLeft: 'auto' }}>
              <Check size={16} />
              Finish
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default AddDeviceWizard
