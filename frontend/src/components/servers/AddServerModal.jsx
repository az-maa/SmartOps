// src/components/servers/AddServerModal.jsx
import React, { useState } from 'react';
import Modal from '../common/Modal';
import Button from '../common/Button';

const AddServerModal = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    name: '',
    ip: '',
    apiKey: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.name.trim()) {
      setError('Server name is required');
      return;
    }

    if (!formData.ip.trim()) {
      setError('IP address is required');
      return;
    }

    // Validate IP format (basic)
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(formData.ip)) {
      setError('Invalid IP address format');
      return;
    }

    setLoading(true);

    try {
      await onAdd(formData.name, formData.ip, formData.apiKey);
      // Reset form
      setFormData({ name: '', ip: '', apiKey: '' });
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to add server');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ name: '', ip: '', apiKey: '' });
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add New Server">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Server Name *
          </label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Web Server 1"
            required
          />
        </div>

        <div>
          <label htmlFor="ip" className="block text-sm font-medium text-gray-700 mb-2">
            IP Address *
          </label>
          <input
            id="ip"
            name="ip"
            type="text"
            value={formData.ip}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., 192.168.1.100"
            required
          />
        </div>

        <div>
          <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
            API Key (Optional)
          </label>
          <input
            id="apiKey"
            name="apiKey"
            type="text"
            value={formData.apiKey}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Leave empty for auto-generation"
          />
          <p className="text-xs text-gray-500 mt-1">
            This key will be used by the monitoring agent
          </p>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button 
            type="button"
            variant="secondary" 
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading}
          >
            {loading ? 'Adding...' : 'Add Server'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default AddServerModal;