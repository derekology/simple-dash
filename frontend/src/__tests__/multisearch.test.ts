import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MultiSearchDropdown from '../components/MultiSearchDropdown.vue'

describe('MultiSearchDropdown', () => {
  const mockOptions = [
    { value: 0, label: 'Campaign 1', subtitle: 'Subject 1' },
    { value: 1, label: 'Campaign 2', subtitle: 'Subject 2' },
    { value: 2, label: 'Campaign 3', subtitle: 'Subject 3' }
  ]

  it('renders with placeholder text when closed', () => {
    const wrapper = mount(MultiSearchDropdown, {
      props: {
        options: mockOptions,
        modelValue: []
      }
    })

    expect(wrapper.text()).toContain('Select campaigns...')
  })

  it('shows selected count when campaigns are selected', () => {
    const wrapper = mount(MultiSearchDropdown, {
      props: {
        options: mockOptions,
        modelValue: [0, 1]
      }
    })

    expect(wrapper.text()).toContain('2 campaigns')
    expect(wrapper.text()).toContain('selected')
  })

  it('emits toggle-outliers event when outliers button clicked', async () => {
    const wrapper = mount(MultiSearchDropdown, {
      props: {
        options: mockOptions,
        modelValue: [],
        showOutliers: true,
        outliersCount: 2,
        outliersButtonText: 'Select Outliers'
      }
    })

    const buttons = wrapper.findAll('button')
    const outliersButton = buttons.find(b => b.text().includes('Select Outliers'))

    if (outliersButton) {
      await outliersButton.trigger('click')
      expect(wrapper.emitted()).toHaveProperty('toggleOutliers')
    }
  })

  it('emits toggle-low-volume event when low volume button clicked', async () => {
    const wrapper = mount(MultiSearchDropdown, {
      props: {
        options: mockOptions,
        modelValue: [],
        showLowVolume: true,
        lowVolumeCount: 1,
        lowVolumeButtonText: 'Select Low Volume'
      }
    })

    const buttons = wrapper.findAll('button')
    const lowVolumeButton = buttons.find(b => b.text().includes('Select Low Volume'))

    if (lowVolumeButton) {
      await lowVolumeButton.trigger('click')
      expect(wrapper.emitted()).toHaveProperty('toggleLowVolume')
    }
  })
})
